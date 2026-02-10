"""Root conftest: work around ROS pytest plugins on system with ROS installed."""

import sys

# Block ROS pytest entry points that cause errors
_blocked = [
    "launch_testing_ros_pytest_entrypoint",
    "launch_testing",
]

for mod_name in _blocked:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = type(sys)("_blocked_" + mod_name)
