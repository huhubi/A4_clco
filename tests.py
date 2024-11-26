import pytest
from pulumi import automation as auto
from pulumi_azure_native import web, storage
import pulumi_azure_native.resources as resources

@pytest.fixture(scope="module")
def stack():
    project_name = "azure-py-appservice"
    stack_name = "testing"

    try:
        stack = auto.select_stack(
            stack_name=stack_name,
            project_name=project_name,
            program=lambda: None,
        )
    except auto.errors.StackNotFoundError:
        stack = auto.create_stack(
            stack_name=stack_name,
            project_name=project_name,
            program=lambda: None,
        )

    stack.up(on_output=print)  # Ensure the stack is updated

    try:
        outputs = stack.outputs()
        resolved_outputs = {key: value.value for key, value in outputs.items()}
        return resolved_outputs
    except Exception as e:
        print(f"Fehler beim Laden der Stack-Outputs: {e}")
        raise e

def test_app_service_plan_is_free(stack):
    # Get the outputs from the stack
    app_service_plan_id = stack["app_service_plan_id"]

    # Fetch the app service plan resource
    app_service_plan = web.AppServicePlan.get("appservice-asp", app_service_plan_id)

    # Check if the app service plan is free and F1
    assert app_service_plan.sku.tier == "Free"
    assert app_service_plan.sku.name == "F1"

def test_storage_account_sku_and_kind(stack):
    # Get the outputs from the stack
    storage_account_id = stack["storage_account_id"]

    # Fetch the storage account resource
    storage_account = storage.StorageAccount.get("storage-account", storage_account_id)

    # Check if the storage account SKU is Standard_LRS and kind is StorageV2
    assert storage_account.sku.name == "Standard_LRS"
    assert storage_account.kind == "StorageV2"

def test_web_app_name_and_type(stack):
    # Get the outputs from the stack
    web_app_id = stack["web_app_id"]

    # Fetch the web app resource
    web_app = web.WebApp.get("web-app", web_app_id)

    # Check the name and type of the web app
    assert web_app.name == "appservice-as"
    assert web_app.kind == "app"

def test_location_is_uksouth(stack):
    # Get the outputs from the stack
    resource_group_name = stack["resource_group_name"]

    # Fetch the resource group resource
    resource_group = resources.ResourceGroup.get("resource-group", resource_group_name)

    # Check if the location is uksouth
    assert resource_group.location == "uksouth"