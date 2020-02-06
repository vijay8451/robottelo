"""Test class for AzureRM Compute Resource

:Requirement: ComputeResources AzureRM

:CaseAutomation: Automated

:CaseLevel: Component

:CaseComponent: ComputeResources-Azure

:TestType: Functional

:CaseImportance: High

:Upstream: No
"""
import pytest

from fauxfactory import gen_string
from nailgun import entities
from robottelo.api.utils import skip_yum_update_during_provisioning
from robottelo.config import settings
from robottelo.constants import (
    AZURERM_FILE_URI,
    AZURERM_RHEL7_FT_IMG_URN,
    AZURERM_RHEL7_UD_IMG_URN,
    AZURERM_RG_DEFAULT,
    AZURERM_PREMIUM_OS_Disk,
    AZURERM_PLATFORM_DEFAULT,
    AZURERM_VM_SIZE_DEFAULT,
)
from robottelo.decorators import (
    tier1,
    tier2,
    tier3,
    upgrade,
)


class TestAzureRMComputeResourceTestCase:
    """Tests for ``api/v2/compute_resources``"""

    @upgrade
    @tier1
    def test_positive_crud_azurerm_cr(self, module_org, module_location, azurerm_settings):
        """Create, Read, Update and Delete AzureRM compute resources

        :id: da081a1f-9614-4918-91cb-c900c40ac121

        :expectedresults: Compute resource should be created, read, updated and deleted

        :CaseImportance: Critical

        :CaseLevel: Component
        """

        # Create CR
        cr_name = gen_string('alpha')
        compresource = entities.AzureRMComputeResource(
            name=cr_name,
            provider='AzureRm',
            tenant=azurerm_settings['tenant'],
            app_ident=azurerm_settings['app_ident'],
            sub_id=azurerm_settings['sub_id'],
            secret_key=azurerm_settings['secret'],
            region=azurerm_settings['region'],
            organization=[module_org],
            location=[module_location],
        ).create()
        assert compresource.name == cr_name
        assert compresource.provider == 'AzureRm'
        assert compresource.tenant == azurerm_settings['tenant']
        assert compresource.app_ident == azurerm_settings['app_ident']
        assert compresource.sub_id == azurerm_settings['sub_id']
        assert compresource.region == azurerm_settings['region']

        # Update CR
        new_cr_name = gen_string('alpha')
        description = gen_string('utf8')
        compresource.name = new_cr_name
        compresource.description = description
        compresource = compresource.update(['name', 'description'])
        assert compresource.name == new_cr_name
        assert compresource.description == description

        # Delete CR
        compresource.delete()
        assert not entities.AzureRMComputeResource().search(
            query={'search': 'name={}'.format(new_cr_name)})

    @upgrade
    @tier2
    def test_positive_create_finish_template_image(self,
                                                   module_architecture,
                                                   module_azurerm_cr,
                                                   module_azurerm_finishimg):
        """ Finish template image along with username is being added in AzureRM CR

        :id: 78facb19-4b27-454b-abc5-2c69c0a6c28a

        :steps:
            1. Create a AzureRM Compute Resource.
            2. Add a finish template based image in it.

        :expectedresults: Finish template image should be added in AzureRM CR along with username

        :CaseImportance: Critical

        :CaseLevel: Integration
        """

        assert module_azurerm_finishimg.architecture.id == module_architecture.id
        assert module_azurerm_finishimg.compute_resource == module_azurerm_cr
        assert module_azurerm_finishimg.username == settings.azurerm.username
        assert module_azurerm_finishimg.uuid == AZURERM_RHEL7_FT_IMG_URN

    @upgrade
    @tier2
    def test_positive_create_cloud_init_image(self,
                                              module_azurerm_cloudimg,
                                              module_azurerm_cr,
                                              module_architecture):
        """Cloud Init template image along with username is being added in AzureRM CR

        :id: 05ea1b20-0dfe-4af3-b1b7-a82604aa1e79

        :steps:
            1. Create a AzureRM Compute Resource.
            2. Add a Cloud init supported image in it.

        :expectedresults: Cloud init image should be added in AzureRM CR along with username

        :CaseLevel: Integration
        """

        assert module_azurerm_cloudimg.architecture.id == module_architecture.id
        assert module_azurerm_cloudimg.compute_resource.id == module_azurerm_cr.id
        assert module_azurerm_cloudimg.username == settings.azurerm.username
        assert module_azurerm_cloudimg.uuid == AZURERM_RHEL7_UD_IMG_URN

    @upgrade
    @tier2
    def test_positive_check_available_networks(self, azurermclient, module_azurerm_cr):
        """Check networks from AzureRM CR are available to select during host provision.

        :id: aee5d077-668e-4f4d-adee-6472f0e4ecaa

        :expectedresults: All the networks from AzureRM CR should be available.

        :CaseLevel: Integration
        """

        cr_nws = module_azurerm_cr.available_networks()
        portal_nws = azurermclient.list_network()
        assert len(portal_nws) == len(cr_nws['results'])


class TestAzureRMHostProvisioningTestCase:
    """ AzureRM Host Provisioning Tests

    """
    @pytest.fixture(scope='class', autouse=True)
    def class_setup(self, request, module_domain, module_azurerm_cr):
        """
        Sets Constants for all the Tests, fixtures which will be later used for assertions
        """
        request.cls.region = settings.azurerm.azure_region
        request.cls.rhel7_ft_img = AZURERM_RHEL7_FT_IMG_URN
        request.cls.rg_default = AZURERM_RG_DEFAULT
        request.cls.premium_os_disk = AZURERM_PREMIUM_OS_Disk
        request.cls.platform = AZURERM_PLATFORM_DEFAULT
        request.cls.vm_size = AZURERM_VM_SIZE_DEFAULT
        request.cls.hostname = gen_string('alpha')
        request.cls.fullhostname = '{}.{}'.format(self.hostname, module_domain.name).lower()

        request.cls.compute_attrs = {
            "resource_group": self.rg_default,
            "vm_size": self.vm_size,
            "username": settings.azurerm.username,
            "password": settings.azurerm.password,
            "platform": self.platform,
            "script_command": 'touch /var/tmp/text.txt',
            "script_uris": AZURERM_FILE_URI,
            "image_id": self.rhel7_ft_img,
        }

        nw_id = module_azurerm_cr.available_networks()['results'][-1]['id']
        request.cls.interfaces_attributes = {
            "0": {
                "compute_attributes": {
                    "public_ip": "Dynamic",
                    "private_ip": "false",
                    "network": nw_id,
                }}}

    @pytest.fixture(scope='class')
    def class_host_ft(self,
                      azurermclient,
                      module_azurerm_finishimg,
                      module_azurerm_cr,
                      module_architecture,
                      module_domain,
                      module_location,
                      module_org,
                      module_os,
                      module_smart_proxy,
                      module_puppet_environment):
        """
        Provisions the host on AzureRM using Finish template
        Later in tests this host will be used to perform assertions
        """

        skip_yum_update_during_provisioning(template='Kickstart default finish')
        host = entities.Host(
            architecture=module_architecture,
            compute_resource=module_azurerm_cr,
            compute_attributes=self.compute_attrs,
            interfaces_attributes=self.interfaces_attributes,
            domain=module_domain,
            organization=module_org,
            operatingsystem=module_os,
            location=module_location,
            name=self.hostname,
            provision_method='image',
            image=module_azurerm_finishimg,
            root_pass=gen_string('alphanumeric'),
            environment=module_puppet_environment,
            puppet_proxy=module_smart_proxy,
            puppet_ca_proxy=module_smart_proxy,
        ).create()
        yield host
        skip_yum_update_during_provisioning(template='Kickstart default finish', reverse=True)
        host.delete()

    @pytest.fixture(scope='class')
    def azureclient_host(self, azurermclient, class_host_ft):
        """Returns the AzureRM Client Host object to perform the assertions"""

        return azurermclient.get_vm(name=class_host_ft.name.split('.')[0])

    @upgrade
    @tier3
    def test_positive_azurerm_host_provisioned(self, class_host_ft, azureclient_host):
        """Host can be provisioned on AzureRM

        :id: ff27905f-fa3c-43ac-b969-9525b32f75f5

        :CaseLevel: Component

        ::CaseImportance: Critical

        :steps:
            1. Create a AzureRM Compute Resource and provision host.

        :expectedresults:
            1. The host should be provisioned on AzureRM
            2. The host name should be the same as given in data to provision the host
            3. The host should show Installed status for provisioned host
            4. The provisioned host should be assigned with external IP
        """

        assert class_host_ft.name == self.fullhostname
        assert class_host_ft.build_status_label == "Installed"
        assert class_host_ft.ip == azureclient_host.ip

    @tier3
    def test_positive_azurerm_host_power_on_off(self, class_host_ft, azureclient_host):
        """Host can be powered on and off

        :id: 9ced29d7-d866-4d0c-ac27-78753b5b5a94

        :CaseLevel: System

        :steps:
            1. Create a AzureRM Compute Resource.
            2. Provision a Host on Azure Cloud using above CR.
            3. Power off the host from satellite.
            4. Power on the host again from satellite.

        :expectedresults:
            1. The provisioned host should be powered off.
            2. The provisioned host should be powered on.
        """

        class_host_ft.power(data={'power_action': 'stop'})
        assert azureclient_host.is_stopped
        class_host_ft.power(data={'power_action': 'start'})
        assert azureclient_host.is_started