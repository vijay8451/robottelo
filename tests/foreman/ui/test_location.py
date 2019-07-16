# -*- encoding: utf-8 -*-
"""Test class for Locations UI

:Requirement: Location

:CaseAutomation: Automated

:CaseLevel: Acceptance

:CaseComponent: OrganizationsLocations

:TestType: Functional

:CaseImportance: High

:Upstream: No
"""

from fauxfactory import gen_ipaddr, gen_string
from nailgun import entities

from robottelo.config import settings
from robottelo.constants import (
    INSTALL_MEDIUM_URL,
    LIBVIRT_RESOURCE_URL,
)
from robottelo.decorators import (
    skip_if_not_set,
    tier2,
    upgrade,
)


@tier2
@upgrade
def test_positive_end_to_end(session):
    """Perform end to end testing for location component

    :id: dba5d94d-0c18-4db0-a9e8-66599bffc5d9

    :expectedresults: All expected CRUD actions finished successfully

    :CaseLevel: Integration

    :CaseImportance: High
    """
    loc_parent = entities.Location().create()
    loc_child_name = gen_string('alpha')
    description = gen_string('alpha')
    updated_name = gen_string('alphanumeric')
    with session:
        session.location.create({
            'name': loc_child_name,
            'parent_location': loc_parent.name,
            'description': description
        })
        location_name = "{}/{}".format(loc_parent.name, loc_child_name)
        assert session.location.search(location_name)[0]['Name'] == location_name
        loc_values = session.location.read(location_name)
        assert loc_values['primary']['parent_location'] == loc_parent.name
        assert loc_values['primary']['name'] == loc_child_name
        assert loc_values['primary']['description'] == description
        session.location.update(location_name, {'primary.name': updated_name})
        location_name = "{}/{}".format(loc_parent.name, updated_name)
        assert session.location.search(location_name)[0]['Name'] == location_name
        session.location.delete(location_name)
        assert not session.location.search(location_name)


@tier2
def test_positive_update_subnet(session):
    """Add/Remove subnet from/to location

    :id: fe70ffba-e594-48d5-b2c5-be93e827cc60

    :expectedresults: subnet is added and removed from the location

    :CaseLevel: Integration
    """
    ip_addres = gen_ipaddr(ip3=True)
    subnet = entities.Subnet(
        network=ip_addres,
        mask='255.255.255.0',
    ).create()
    loc = entities.Location().create()
    with session:
        subnet_name = '{0} ({1}/{2})'.format(
            subnet.name, subnet.network, subnet.cidr)
        session.location.update(
            loc.name, {'subnets.resources.assigned': [subnet_name]})
        loc_values = session.location.read(loc.name)
        assert loc_values['subnets']['resources']['assigned'][0] == subnet_name
        session.location.update(
            loc.name, {'subnets.resources.unassigned': [subnet_name]})
        loc_values = session.location.read(loc.name)
        assert len(loc_values['subnets']['resources']['assigned']) == 0
        assert subnet_name in loc_values['subnets']['resources']['unassigned']


@tier2
def test_positive_update_domain(session):
    """Add/Remove domain from/to a Location

    :id: 4f50f5cb-64eb-4790-b4c5-62d67669f48f

    :expectedresults: Domain is added and removed from the location

    :CaseLevel: Integration
    """
    domain = entities.Domain().create()
    loc = entities.Location().create()
    with session:
        session.location.update(
            loc.name, {'domains.resources.assigned': [domain.name]})
        loc_values = session.location.read(loc.name)
        assert loc_values['domains']['resources']['assigned'][0] == domain.name
        session.location.update(
            loc.name, {'domains.resources.unassigned': [domain.name]})
        loc_values = session.location.read(loc.name)
        assert len(loc_values['domains']['resources']['assigned']) == 0
        assert domain.name in loc_values['domains']['resources']['unassigned']


@tier2
def test_positive_update_user(session):
    """Add new user and then remove it from location

    :id: bf9b3fc2-6193-4edc-aaec-cd7b87f0804c

    :expectedresults: User successfully added and then removed from
        location resources

    :CaseLevel: Integration
    """
    user = entities.User().create()
    loc = entities.Location().create()
    with session:
        session.location.update(
            loc.name, {'users.resources.assigned': [user.login]})
        loc_values = session.location.read(loc.name)
        assert loc_values['users']['resources']['assigned'][0] == user.login
        session.location.update(
            loc.name, {'users.resources.unassigned': [user.login]})
        loc_values = session.location.read(loc.name)
        assert len(loc_values['users']['resources']['assigned']) == 0
        assert user.login in loc_values['users']['resources']['unassigned']


@tier2
def test_positive_update_hostgroup(session):
    """Add/Remove host group from/to location.

    :id: e998d20c-e201-4675-b45f-8768f59584da

    :expectedresults: hostgroup is removed and then added to the location

    :CaseLevel: Integration
    """
    hostgroup = entities.HostGroup().create()
    loc = entities.Location().create()
    with session:
        session.location.update(
            loc.name,
            {'host_groups.all_hostgroups': False,
             'host_groups.resources.unassigned': [hostgroup.name]}
        )

        loc_values = session.location.read(loc.name)
        assert loc_values[
            'host_groups']['resources']['unassigned'][0] == hostgroup.name
        session.location.update(
            loc.name, {'host_groups.resources.assigned': [hostgroup.name]})
        new_loc_values = session.location.read(loc.name)
        assert len(new_loc_values['host_groups']['resources']['assigned']) == \
            len(loc_values['host_groups']['resources']['assigned']) + 1
        assert hostgroup.name in new_loc_values[
            'host_groups']['resources']['assigned']


@tier2
def test_positive_add_org(session):
    """Add a organization by using the location name

    :id: 27d56d64-6866-46b6-962d-1ac2a11ae136

    :expectedresults: organization is added to location

    :CaseLevel: Integration
    """
    org = entities.Organization().create()
    loc = entities.Location().create()
    with session:
        session.location.update(
            loc.name, {'organizations.resources.assigned': [org.name]})
        loc_values = session.location.read(loc.name)
        assert loc_values[
            'organizations']['resources']['assigned'][0] == org.name


@tier2
def test_update_environment(session):
    """Add/Remove environment from/to location

    :id: bbca1af0-a31f-4096-bc6e-bb341ffed575

    :expectedresults: environment is added and removed from the location

    :CaseLevel: Integration
    """
    env = entities.Environment().create()
    loc = entities.Location().create()
    with session:
        session.location.update(
            loc.name, {'environments.resources.assigned': [env.name]})
        loc_values = session.location.read(loc.name)
        assert loc_values[
            'environments']['resources']['assigned'][0] == env.name
        session.location.update(
            loc.name, {'environments.resources.unassigned': [env.name]})
        loc_values = session.location.read(loc.name)
        assert len(loc_values['environments']['resources']['assigned']) == 0
        assert env.name in loc_values[
            'environments']['resources']['unassigned']


@skip_if_not_set('compute_resources')
@tier2
def test_positive_update_compresource(session):
    """Add/Remove compute resource from/to location

    :id: 1d24414a-666d-490d-89b9-cd0704684cdd

    :expectedresults: compute resource is added and removed from the location

    :CaseLevel: Integration
    """
    url = (
            LIBVIRT_RESOURCE_URL % settings.compute_resources.libvirt_hostname)
    resource = entities.LibvirtComputeResource(url=url).create()
    resource_name = resource.name + ' (Libvirt)'
    loc = entities.Location().create()
    with session:
        session.location.update(
            loc.name,
            {'compute_resources.resources.assigned': [resource_name]}
        )
        loc_values = session.location.read(loc.name)
        assert loc_values['compute_resources'][
                   'resources']['assigned'][0] == resource_name
        session.location.update(
            loc.name,
            {'compute_resources.resources.unassigned': [resource_name]}
        )
        loc_values = session.location.read(loc.name)
        assert len(
            loc_values['compute_resources']['resources']['assigned']) == 0
        assert resource_name in loc_values[
            'compute_resources']['resources']['unassigned']


@tier2
def test_positive_update_medium(session):
    """Add/Remove medium from/to location

    :id: 738c5ff1-ef09-466f-aaac-64f194cac78d

    :expectedresults: medium is added and removed from the location

    :CaseLevel: Integration
    """
    media = entities.Media(
        path_=INSTALL_MEDIUM_URL % gen_string('alpha', 6),
        os_family='Redhat',
    ).create()
    loc = entities.Location().create()
    with session:
        session.location.update(
            loc.name, {'media.resources.assigned': [media.name]})
        loc_values = session.location.read(loc.name)
        assert loc_values['media']['resources']['assigned'][0] == media.name
        session.location.update(
            loc.name, {'media.resources.unassigned': [media.name]})
        loc_values = session.location.read(loc.name)
        assert len(loc_values['media']['resources']['assigned']) == 0
        assert media.name in loc_values['media']['resources']['unassigned']


@tier2
def test_positive_update_template(session):
    """Add/Remove template from/to location

    :id: 8faf60d1-f4d6-4a58-a484-606a42957ce7

    :expectedresults: config template is removed and then added to the location

    :CaseLevel: Integration
    """
    template = entities.ProvisioningTemplate().create()
    loc = entities.Location().create()
    with session:
        session.location.update(
            loc.name,
            {'provisioning_templates.all_templates': False,
             'provisioning_templates.resources.unassigned': [template.name]}
        )
        loc_values = session.location.read(loc.name)
        assert loc_values['provisioning_templates']['resources'][
                   'unassigned'][0] == template.name
        session.location.update(loc.name, {
            'provisioning_templates.resources.assigned': [template.name]})
        new_loc_values = session.location.read(loc.name)
        assert len(new_loc_values[
                       'provisioning_templates']['resources']['assigned']) == \
            len(loc_values[
                    'provisioning_templates']['resources']['assigned']) + 1
        assert template.name in new_loc_values[
            'provisioning_templates']['resources']['assigned']
