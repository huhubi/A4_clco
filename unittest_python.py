import pulumi
import pulumi_azure_native.resources as resources
import pulumi_azure_native.storage as storage
import pulumi_azure_native.web as web
import pulumi_azure_native.sql as sql
import pulumi_azure_native.insights as insights
from pulumi_azure_native.storage import BlobContainer
import unittest_python

class TestingPulumiProgram(unittest_python.TestCase):
    @pulumi.runtime.test
    def test_resource_group_created(self):
        resource_group = resources.ResourceGroup("appservicerg")

        def check_resource_group(name):
            self.assertEqual(name, "appservicerg")

        resource_group.name.apply(check_resource_group)

    @pulumi.runtime.test
    def test_storage_account_created(self):
        resource_group = resources.ResourceGroup("appservicerg")
        storage_account = storage.StorageAccount(
            "appservicesa",
            resource_group_name=resource_group.name,
            kind=storage.Kind.STORAGE_V2,
            sku=storage.SkuArgs(name=storage.SkuName.STANDARD_LRS))

        def check_storage_account(args):
            self.assertEqual(args["kind"], "StorageV2")
            self.assertEqual(args["sku"].name, "Standard_LRS")

        pulumi.Output.all(
            storage_account.kind, storage_account.sku
        ).apply(lambda args: check_storage_account({"kind": args[0], "sku": args[1]}))

    @pulumi.runtime.test
    def test_sql_server_created(self):
        resource_group = resources.ResourceGroup("appservicerg")
        sql_server = sql.Server(
            "appservice-sql",
            resource_group_name=resource_group.name,
            administrator_login="pulumi",
            administrator_login_password="testpassword",
            version="12.0")

        def check_sql_server(args):
            self.assertEqual(args["administrator_login"], "pulumi")
            self.assertEqual(args["version"], "12.0")

        pulumi.Output.all(
            sql_server.administrator_login, sql_server.version
        ).apply(lambda args: check_sql_server({"administrator_login": args[0], "version": args[1]}))

    @pulumi.runtime.test
    def test_web_app_created(self):
        resource_group = resources.ResourceGroup("appservicerg")
        app_service_plan = web.AppServicePlan(
            "appservice-asp",
            resource_group_name=resource_group.name,
            kind="App",
            sku=web.SkuDescriptionArgs(
                tier="Free",
                name="F1",
            ))

        app_insights = insights.Component(
            "appservice-ai",
            application_type=insights.ApplicationType.WEB,
            kind="web",
            resource_group_name=resource_group.name)

        web_app = web.WebApp(
            "appservice-as",
            resource_group_name=resource_group.name,
            server_farm_id=app_service_plan.id,
            site_config=web.SiteConfigArgs(
                app_settings=[
                    web.NameValuePairArgs(
                        name="APPINSIGHTS_INSTRUMENTATIONKEY",
                        value=app_insights.instrumentation_key
                    )
                ]
            )
        )

        def check_web_app(app_name):
            self.assertEqual(app_name, "appservice-as")

        web_app.name.apply(check_web_app)

    @pulumi.runtime.test
    def test_blob_container_created(self):
        resource_group = resources.ResourceGroup("appservicerg")
        storage_account = storage.StorageAccount(
            "appservicesa",
            resource_group_name=resource_group.name,
            kind=storage.Kind.STORAGE_V2,
            sku=storage.SkuArgs(name=storage.SkuName.STANDARD_LRS))

        blob_container = BlobContainer(
            "appservice-c",
            account_name=storage_account.name,
            public_access=storage.PublicAccess.NONE,
            resource_group_name=resource_group.name)

        def check_blob_container(public_access):
            self.assertEqual(public_access, storage.PublicAccess.NONE)

        blob_container.public_access.apply(check_blob_container)

if __name__ == "__main__":
    unittest_python.main()
