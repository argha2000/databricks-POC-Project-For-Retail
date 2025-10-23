# Upgrade Databricks SDK to the latest version and restart Python to see updated packages
%pip install --upgrade databricks-sdk==0.49.0
%restart_python

from databricks.sdk.service.jobs import JobSettings as Job


End_to_End_Pipeline = Job.from_dict(
    {
        "name": "End to End Pipeline",
        "tasks": [
            {
                "task_key": "bronze_incremental",
                "run_job_task": {
                    "job_id": 748769287483930,
                },
            },
            {
                "task_key": "Silver_customers",
                "depends_on": [
                    {
                        "task_key": "bronze_incremental",
                    },
                ],
                "notebook_task": {
                    "notebook_path": "/Workspace/Users/arghabhattacharjee999@gmail.com/databricks_Project/customers_silver_layer",
                    "source": "WORKSPACE",
                },
            },
            {
                "task_key": "Silver_orders",
                "depends_on": [
                    {
                        "task_key": "bronze_incremental",
                    },
                ],
                "notebook_task": {
                    "notebook_path": "/Workspace/Users/arghabhattacharjee999@gmail.com/databricks_Project/order_silver_layer",
                    "source": "WORKSPACE",
                },
            },
            {
                "task_key": "Silver_products",
                "depends_on": [
                    {
                        "task_key": "bronze_incremental",
                    },
                ],
                "notebook_task": {
                    "notebook_path": "/Workspace/Users/arghabhattacharjee999@gmail.com/databricks_Project/products_silver_layer",
                    "source": "WORKSPACE",
                },
            },
            {
                "task_key": "Gold_Customers",
                "depends_on": [
                    {
                        "task_key": "Silver_products",
                    },
                    {
                        "task_key": "Silver_orders",
                    },
                    {
                        "task_key": "Silver_customers",
                    },
                ],
                "notebook_task": {
                    "notebook_path": "/Workspace/Users/arghabhattacharjee999@gmail.com/databricks_Project/customers_gold_layer",
                    "source": "WORKSPACE",
                },
            },
            {
                "task_key": "Gold_products",
                "depends_on": [
                    {
                        "task_key": "Silver_orders",
                    },
                    {
                        "task_key": "Silver_customers",
                    },
                    {
                        "task_key": "Silver_products",
                    },
                ],
                "pipeline_task": {
                    "pipeline_id": "2313d399-df26-4e59-bbbb-36ab3fe59a2a",
                    "full_refresh": True,
                },
            },
            {
                "task_key": "Fact_Orders",
                "depends_on": [
                    {
                        "task_key": "Gold_Customers",
                    },
                    {
                        "task_key": "Gold_products",
                    },
                    {
                        "task_key": "Silver_orders",
                    },
                ],
                "notebook_task": {
                    "notebook_path": "/Workspace/Users/arghabhattacharjee999@gmail.com/databricks_Project/orders_gold_layer",
                    "source": "WORKSPACE",
                },
            },
        ],
        "queue": {
            "enabled": True,
        },
        "performance_target": "PERFORMANCE_OPTIMIZED",
    }
)

from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
w.jobs.reset(new_settings=End_to_End_Pipeline, job_id=952696766942746)
# or create a new job using: w.jobs.create(**End_to_End_Pipeline.as_shallow_dict())
