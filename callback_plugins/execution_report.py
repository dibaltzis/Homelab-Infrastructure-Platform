from ansible.plugins.callback import CallbackBase
from ansible.utils.display import Display
import json
import time
import os
from datetime import datetime

display = Display()


class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'execution_report'
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.start_time = time.time()
        self.role_data = {}
        self.task_count = 0
        self.playbook_name = "unknown"

    def v2_playbook_on_start(self, playbook):
        self.playbook_name = playbook._file_name

    # ---------- TASK EVENTS ----------

    def v2_runner_on_ok(self, result):
        self.task_count += 1
        role = self._get_role(result)
        self._init_role(role)

        if role and result._result.get("changed", False):
            self.role_data[role]["changed"] += 1

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.task_count += 1
        role = self._get_role(result)
        self._init_role(role)

        if role:
            self.role_data[role]["failed"] += 1

    def v2_runner_on_skipped(self, result):
        self.task_count += 1

    # ---------- FINAL STATS ----------

    def v2_playbook_on_stats(self, stats):

        end_time = time.time()
        duration = round(end_time - self.start_time, 2)

        hosts = list(stats.processed.keys())

        total_failed = sum(
            stats.summarize(h)["failures"] for h in hosts
        )

        total_changed = sum(
            stats.summarize(h)["changed"] for h in hosts
        )

        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "duration_seconds": duration,
            "overall_status": "FAILED" if total_failed > 0 else "SUCCESS",
            "total_hosts": len(hosts),
            "total_tasks": self.task_count,
            "total_changed": total_changed,
            "total_failed": total_failed,
            "roles": self.role_data
        }

        report["environment"] = os.getenv("ENVIRONMENT", "unknown")
        report["playbook"] = getattr(self, "playbook_name", "unknown")

        # ---------- Collect custom stats ----------

        custom_stats = {}

        if getattr(stats, "custom", None):
            custom_stats.update(stats.custom)

        if getattr(stats, "_custom", None):
            custom_stats.update(stats._custom)

        rclone_data = {}

        for key, value in custom_stats.items():
            if key.startswith("rclone_"):
                section = key.replace("rclone_", "", 1)
                rclone_data[section] = value

        if rclone_data:
            report["rclone-restore"] = rclone_data

        # ---------- Write JSON report ----------

        os.makedirs("reports", exist_ok=True)

        filename = f"reports/execution_report_{int(self.start_time)}.json"

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        latest_path = "reports/execution_report_latest.json"

        with open(latest_path, "w") as f:
            json.dump(report, f, indent=2)

        # ---------- Pretty Console Summary ----------

        summary_lines = []
        summary_lines.append("")
        summary_lines.append("========== EXECUTION REPORT ==========")
        summary_lines.append(f"Status: {report['overall_status']}")
        summary_lines.append(f"Duration: {duration}s")
        summary_lines.append(f"Hosts: {len(hosts)}")
        summary_lines.append(f"Tasks: {self.task_count}")
        summary_lines.append(f"Changed: {total_changed}")
        summary_lines.append(f"Failed: {total_failed}")
        summary_lines.append("")

        summary_lines.append("Per Role:")

        for role, data in self.role_data.items():
            summary_lines.append(
                f"  - {role}: changed={data['changed']} failed={data['failed']}"
            )

        # ---------- Rclone Section ----------

        if rclone_data:

            summary_lines.append("")
            summary_lines.append("Rclone Summary:")

            for section, items in rclone_data.items():

                title = section.replace("_", " ").title()
                summary_lines.append(f"{title}:")

                if isinstance(items, list):

                    for entry in items:

                        summary_lines.append(f"  Service: {entry.get('name')}")
                        summary_lines.append(f"    Source: {entry.get('source')}")
                        summary_lines.append(f"    Destination: {entry.get('destination')}")
                        summary_lines.append(f"    Date: {entry.get('date')}")
                        summary_lines.append(f"    Status: {entry.get('status')}")
                        summary_lines.append(f"    Forced: {entry.get('forced')}")
                        summary_lines.append("")

        summary_lines.append("======================================")
        summary_lines.append(f"Report written to {filename}")
        summary_lines.append("")

        execution_summary = "\n".join(summary_lines)

        #display.display(execution_summary)

    # ---------- HELPERS ----------

    def _get_role(self, result):

        if not result._task or not result._task._role:
            return None

        return result._task._role.get_name()

    def _init_role(self, role):

        if role and role not in self.role_data:
            self.role_data[role] = {
                "changed": 0,
                "failed": 0
            }