#!/usr/bin/python
# SPDX-FileCopyrightText: 2021 Kevin P. Fleming <kevin@km6g.us>
# SPDX-License-Identifier: Apache-2.0
# -*- coding: utf-8 -*-

import sys

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.kpfleming.powerdns_auth.plugins.module_utils.api_wrapper import (
    APIWrapper,
    api_exception_handler,
)

assert sys.version_info >= (3, 9), "This module requires Python 3.9 or newer."

DOCUMENTATION = """
%YAML 1.2
---
module: pdns_auth_zone

short_description: Manages a zone in a PowerDNS Authoritative server

description:
  - This module allows a task to manage the presence and configuration
    of a zone in a PowerDNS Authoritative server.

requirements:
  - bravado

extends_documentation_fragment:
  - kpfleming.powerdns_auth.api_details

options:
  state:
    description:
      - If V(present) the zone will be created if necessary; if it
        already exists, its configuration will be updated to match
        the provided properties.
      - If V(absent) the zone will be removed it if exists.
      - If V(exists) the zone's existence will be checked, but it
        will not be modified. Any configuration properties provided
        will be ignored.
      - If V(notify) and O(properties.kind=Master), then NOTIFY will be sent to
        the zone's slaves.
      - If V(notify) and O(properties.kind=Slave), then the slave zone will be
        updated as if a NOTIFY had been received.
      - If V(retrieve) and O(properties.kind=Slave), then the slave zone will be
        retrieved from the master.
    choices: [ 'present', 'absent', 'exists', 'notify', 'retrieve' ]
    type: str
    required: false
    default: 'present'
  name:
    description:
      - Name of the zone to be managed.
    type: str
    required: true
  properties:
    description:
      - Zone properties. Ignored when O(state=exists), O(state=absent), O(state=notify),
        or O(state=retrieve).
    type: dict
    suboptions:
      kind:
        description:
          - Zone kind.
          - V(Producer) and V(Consumer) are only supported in server version
            4.7.0 or later.
        choices: [ 'Native', 'Master', 'Slave', 'Producer', 'Consumer' ]
        type: str
        required: true
      account:
        description:
          - Optional string used for local policy.
        type: str
      catalog:
        description:
          - Optional zone name, indicating that this zone should be a member of the specified
            catalog zone.
          - Must be an absolute zone name (ending with '.').
          - Only supported in server version 4.7.0 or later.
        type: str
      nameservers:
        description:
          - List of nameserver names to be listed in NS records for zone.
          - Only used when O(properties.kind=Native), O(properties.kind=Master),
            or O(properties.kind=Producer).
          - Only used when zone is being created (O(state=present) and zone is not present).
          - Must be absolute names (ending with '.').
        type: list
        elements: str
      ttl:
        description:
          - Time to live for SOA and NS records.
          - Only used when O(properties.kind=Native), O(properties.kind=Master),
            or O(properties.kind=Producer).
          - Only used when zone is being created (O(state=present) and zone is not present).
        type: int
        required: false
        default: 86400
      soa:
        description:
          - SOA record fields.
          - Only used when O(properties.kind=Native), O(properties.kind=Master),
            or O(properties.kind=Producer).
          - Only used when zone is being created (O(state=present) and zone is not present).
        type: dict
        suboptions:
          mname:
            description:
              - DNS name (absolute, ending with '.') of primary name server for the zone.
            type: str
            required: true
          rname:
            description:
              - Email address of the 'responsible party' for the zone, formatted as a
                DNS name (absolute, ending with '.').
            type: str
            required: true
          serial:
            description:
              - Initial serial number.
            type: int
            required: false
            default: 1
          refresh:
            description:
              - Number of seconds after which secondary name servers should query the primary
                for the SOA record, to detect zone changes.
            type: int
            required: false
            default: 86400
          retry:
            description:
              - Number of seconds after which secondary name servers should retry to request
                the serial number from the primary if the primary does not respond.
              - Must be less than O(properties.soa.refresh).
            type: int
            required: false
            default: 7200
          expire:
            description:
              - Number of seconds after which secondary name servers should stop answering
                requests for this zone if the primary does not respond.
              - Must be bigger than the sum of O(properties.soa.refresh) and
                O(properties.soa.retry).
            type: int
            required: false
            default: 3600000
          ttl:
            description:
              - Time to live for purposes of negative caching.
            type: int
            required: false
            default: 172800
      rrsets:
        description:
          - Resource Record Set.
            Only used when O(properties.kind=Native), O(properties.kind=Master),
            or O(properties.kind=Producer).
          - Only used when zone is being created (O(state=present) and zone is not present).
          - SOA records are not permitted.
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - Name for record set (e.g. "www.powerdns.com.").
              - Must be absolute names (ending with '.').
            type: str
            required: true
          type:
            description:
              - Type of resource record (e.g. "A", "PTR", "MX").
            type: str
            required: true
          ttl:
            description:
              - TTL of the records, in seconds.
            type: int
            default: 3600
          records:
            description:
              - Represents a list of records.
            required: true
            type: list
            elements: dict
            suboptions:
              disabled:
                description:
                  - Whether or not this record is disabled.
                type: bool
                default: false
              content:
                description:
                  - The content of resource record.
                type: str
                required: true
      masters:
        description:
          - List of IPv4 or IPv6 addresses which are masters for this zone.
            Only used when O(properties.kind=Slave) or O(properties.kind=Consumer).
        type: list
        elements: str
      master_tsig_key_ids:
        description:
          - The id of the TSIG keys used for master operation in this zone.
            Only used when O(properties.kind=Master) or O(properties.kind=Producer).
        type: list
        elements: str
      slave_tsig_key_ids:
        description:
          - The id of the TSIG keys used for slave operation in this zone.
            Only used when O(properties.kind=Slave) or O(properties.kind=Consumer).
        type: list
        elements: str
  metadata:
    description:
      - Zone metadata. Ignored when O(state=exists), O(state=absent), O(state=notify),
        or O(state=retrieve).
    type: dict
    suboptions:
      allow_axfr_from:
        description:
          - List of IPv4 and/or IPv6 subnets (or the special value AUTO-NS) from which AXFR
            requests will be accepted.
        type: list
        elements: str
      allow_dnsupdate_from:
        description:
          - List of IPv4 and/or IPv6 subnets from which DNSUPDATE requests will be accepted.
        type: list
        elements: str
      also_notify:
        description:
          - List of IPv4 and/or IPv6 addresses (with optional port numbers) which will receive
            NOTIFY for updates.
        type: list
        elements: str
      api_rectify:
        description:
          - Rectify zone's record sets after changes made through the API.
        type: bool
      axfr_source:
        description:
          - IPv4 or IPv6 address to be used as the source address for AXFR and IXFR requests.
        type: str
      axfr_master_tsig:
        description:
          - List of TSIG keys used to validate NOTIFY requests from zone masters and to
            sign AXFR/IXFR requests to zone masters.
          - "Note: only the first key in the list will be used."
        type: list
        elements: str
      forward_dnsupdate:
        description:
          - Forward DNSUPDATE requests to one of the zone's masters.
        type: bool
      gss_acceptor_principal:
        description:
          - Kerberos/GSS principal which identifies this server.
        type: str
      gss_allow_axfr_principal:
        description:
          - Kerberos/GSS principal which must be included in AXFR requests.
        type: str
      ixfr:
        description:
          - Attempt IXFR when retrieving zone updates.
        type: bool
      notify_dnsupdate:
        description:
          - Send a NOTIFY to all slave servers after processing a DNSUPDATE request.
        type: bool
      nsec3narrow:
        description:
          - Indicates that this zone operations in NSEC3 'narrow' mode.
        type: bool
      nsec3param:
        description:
          - NSEC3 parameters for the zone when DNSSEC is used.
        type: str
      publish_cdnskey:
        description:
          - Publish CDNSKEY records of the KSKs for the zone.
        type: bool
      publish_cds:
        description:
          - List of signature algorithm numbers for CDS records of the KSKs for the zone.
        type: list
        elements: str
      slave_renotify:
        description:
          - Re-send NOTIFY to slaves after receiving AXFR from master.
          - If this is not set, the 'slave-renotify' setting in the server configuration
            will be applied to the zone.
        type: bool
      soa_edit:
        description:
          - Method to update the serial number in the SOA record when serving it.
        type: str
        choices: [ 'INCREMENT-WEEKS', 'INCEPTION-EPOCH', 'INCEPTION-INCREMENT', 'EPOCH', 'NONE' ]
      soa_edit_api:
        description:
          - Method to update the serial number in the SOA record after an API edit.
        type: str
        choices: [ 'DEFAULT', 'INCREASE', 'EPOCH', 'SOA-EDIT', 'SOA-EDIT-INCREASE' ]
        default: 'DEFAULT'
      soa_edit_dnsupdate:
        description:
          - Method to update the serial number in the SOA record after a DNSUPDATE.
        type: str
        choices: [ 'DEFAULT', 'INCREASE', 'EPOCH', 'SOA-EDIT', 'SOA-EDIT-INCREASE' ]
        default: 'DEFAULT'
      tsig_allow_axfr:
        description:
          - List of TSIG keys used to sign NOTIFY requests and to validate
            AXFR/IXFR requests.
          - "Note: only the first key in the list will be used."
        type: list
        elements: str
      tsig_allow_dnsupdate:
        description:
          - List of TSIG keys for which DNSUPDATE requests will be accepted.
        type: list
        elements: str

author:
  - Kevin P. Fleming (@kpfleming)
"""

EXAMPLES = """
%YAML 1.2
---
- name: check that zone exists
  pdns_auth_zone:
    name: d1.example.
    state: exists
    api_key: 'foobar'

- name: check that zone exists on a non-default server
  pdns_auth_zone:
    name: d1.example.
    state: exists
    api_key: 'foobar'
    api_url: 'http://pdns.server.example:80'

- name: send NOTIFY to slave servers for zone
  pdns_auth_zone:
    name: d1.example.
    state: notify
    api_key: 'foobar'

- name: retrieve zone from master server
  pdns_auth_zone:
    name: d1.example.
    state: retrieve
    api_key: 'foobar'

- name: create native zone
  pdns_auth_zone:
    name: d2.example.
    state: present
    api_key: 'foobar'
    properties:
      kind: 'Native'
      nameservers:
        - 'ns1.example.'
      soa:
        mname: 'localhost.'
        rname: 'hostmaster.localhost.'
    metadata:
      allow_axfr_from: ['AUTO-NS']
      axfr_source: '127.0.0.1'

- name: change native zone to master
  pdns_auth_zone:
    name: d2.example.
    state: present
    api_key: 'foobar'
    properties:
      kind: 'Master'

- name: delete zone
  pdns_auth_zone:
    name: d2.example.
    state: absent
    api_key: 'foobar'

- name: create slave zone
  pdns_auth_zone:
    name: d3.example.
    state: present
    api_key: 'foobar'
    properties:
      kind: 'Slave'
      masters:
        - '1.1.1.1'
        - '::1'
"""

RETURN = """
%YAML 1.2
---
zone:
  description: Information about the zone
  returned: always
  type: dict
  contains:
    name:
      description: Name
      returned: always
      type: str
    exists:
      description: Indicate whether the zone exists
      returned: always
      type: bool
    kind:
      description: Kind
      returned: when present
      type: str
      choices: [ Native, Master, Slave, Producer, Consumer ]
    serial:
      description: Serial number from SOA record
      returned: when present
      type: int
    account:
      description: Account label
      returned: always
      type: str
    catalog:
      description: Name of catalog zone containing this zone
      returned: when present
      type: str
    dnssec:
      description: Flag indicating whether zone is signed with DNSSEC
      returned: when present
      type: bool
    masters:
      description: IP addresses of masters (only for Slave and Consumer zones)
      returned: when present
      type: list
      elements: str
    master_tsig_key_ids:
      description: The id of the TSIG keys used for master operation in this zone.
      returned: when present
      type: list
      elements: str
    slave_tsig_key_ids:
      description: The id of the TSIG keys used for slave operation in this zone.
      returned: when present
      type: list
      elements: str
    metadata:
      description: Zone metadata
      returned: when present
      type: dict
      contains:
        allow_axfr_from:
          description:
            - List of IPv4 and/or IPv6 subnets (or the special value AUTO-NS) from which AXFR
              requests will be accepted.
          type: list
          elements: str
        allow_dnsupdate_from:
          description:
            - List of IPv4 and/or IPv6 subnets from which DNSUPDATE requests will be accepted.
          type: list
          elements: str
        also_notify:
          description:
            - List of IPv4 and/or IPv6 addresses (with optional port numbers) which will receive
              NOTIFY for updates.
          type: list
          elements: str
        api_rectify:
          description:
            - Rectify zone's record sets after changes made through the API.
          type: bool
        axfr_master_tsig:
          description:
            - List of TSIG keys used to validate NOTIFY requests from zone masters and to
              sign AXFR/IXFR requests to zone masters.
          type: list
          elements: str
        axfr_source:
          description:
            - IPv4 or IPv6 address to be used as the source address for AXFR and IXFR requests.
          type: str
        forward_dnsupdate:
          description:
            - Forward DNSUPDATE requests to one of the zone's masters.
          type: bool
        gss_acceptor_principal:
          description:
            - Kerberos/GSS principal which identifies this server.
          type: str
        gss_allow_axfr_principal:
          description:
            - Kerberos/GSS principal which must be included in AXFR requests.
          type: str
        ixfr:
          description:
            - Attempt IXFR when retrieving zone updates.
          type: bool
        lua_axfr_script:
          description:
            - Script to be used to edit incoming AXFR requests; use 'NONE' to override a globally
              configured script.
          type: str
        notify_dnsupdate:
          description:
            - Send a NOTIFY to all slave servers after processing a DNSUPDATE request.
          type: bool
        nsec3narrow:
          description:
            - Indicates that this zone operations in NSEC3 'narrow' mode.
          type: bool
        nsec3param:
          description:
            - NSEC3 parameters for the zone when DNSSEC is used.
          type: str
        publish_cdnskey:
          description:
            - Publish CDNSKEY records of the KSKs for the zone.
          type: bool
        publish_cds:
          description:
            - List of signature algorithm numbers for CDS records of the KSKs for the zone.
          type: list
          elements: str
        presigned:
          description:
            - Indicates that this zone zone carries DNSSEC RRSIGs, and is presigned.
          type: bool
        slave_renotify:
          description:
            - Re-send NOTIFY to slaves after receiving AXFR from master.
          type: bool
        soa_edit:
          description:
            - Method to update the serial number in the SOA record when serving it.
          type: str
          choices: [ 'INCREMENT-WEEKS', 'INCEPTION-EPOCH', 'INCEPTION-INCREMENT', 'EPOCH', 'NONE' ]
        soa_edit_api:
          description:
            - Method to update the serial number in the SOA record after an API edit.
          type: str
          choices: [ 'DEFAULT', 'INCREASE', 'EPOCH', 'SOA-EDIT', 'SOA-EDIT-INCREASE' ]
        soa_edit_dnsupdate:
          description:
            - Method to update the serial number in the SOA record after a DNSUPDATE.
          type: str
          choices: [ 'DEFAULT', 'INCREASE', 'EPOCH', 'SOA-EDIT', 'SOA-EDIT-INCREASE' ]
        tsig_allow_axfr:
          description:
            - List of TSIG keys used to sign NOTIFY requests and to validate
              AXFR/IXFR requests.
          type: list
          elements: str
        tsig_allow_dnsupdate:
          description:
            - List of TSIG keys for which DNSUPDATE requests will be accepted.
          type: list
          elements: str
"""


class APIZoneWrapper(APIWrapper):
    def __init__(self, *, module, result, object_type, zone_id):
        super().__init__(module=module, result=result, object_type=object_type)
        self.zone_id = zone_id

    @api_exception_handler
    def axfrRetrieveZone(self):  # noqa: N802
        return self.raw_api.axfrRetrieveZone(
            server_id=self.server_id,
            zone_id=self.zone_id,
        ).result()

    @api_exception_handler
    def createZone(self, **kwargs):  # noqa: N802
        return self.raw_api.createZone(server_id=self.server_id, rrsets=False, **kwargs).result()

    @api_exception_handler
    def deleteZone(self):  # noqa: N802
        return self.raw_api.deleteZone(server_id=self.server_id, zone_id=self.zone_id).result()

    @api_exception_handler
    def listZone(self):  # noqa: N802
        return self.raw_api.listZone(
            server_id=self.server_id,
            zone_id=self.zone_id,
            rrsets=False,
        ).result()

    @api_exception_handler
    def listZones(self, **kwargs):  # noqa: N802
        return self.raw_api.listZones(server_id=self.server_id, **kwargs).result()

    @api_exception_handler
    def notifyZone(self):  # noqa: N802
        return self.raw_api.notifyZone(server_id=self.server_id, zone_id=self.zone_id).result()

    @api_exception_handler
    def putZone(self, **kwargs):  # noqa: N802
        return self.raw_api.putZone(
            server_id=self.server_id,
            zone_id=self.zone_id,
            **kwargs,
        ).result()


class APIZoneMetadataWrapper(APIWrapper):
    def __init__(self, *, module, result, object_type, zone_id):
        super().__init__(module=module, result=result, object_type=object_type)
        self.zone_id = zone_id

    @api_exception_handler
    def deleteMetadata(self, **kwargs):  # noqa: N802
        return self.raw_api.deleteMetadata(
            server_id=self.server_id,
            zone_id=self.zone_id,
            **kwargs,
        ).result()

    @api_exception_handler
    def listMetadata(self):  # noqa: N802
        return self.raw_api.listMetadata(server_id=self.server_id, zone_id=self.zone_id).result()

    @api_exception_handler
    def modifyMetadata(self, **kwargs):  # noqa: N802
        return self.raw_api.modifyMetadata(
            server_id=self.server_id,
            zone_id=self.zone_id,
            **kwargs,
        ).result()


class Metadata:
    map_by_api_kind = {}
    map_by_meta = {}

    def __init__(self, api_kind):
        self.api_kind = api_kind
        self.meta = api_kind.lower().replace("-", "_")
        self.immutable = False
        self.map_by_api_kind[self.api_kind] = self
        self.map_by_meta[self.meta] = self

    def value_or_default(self, value):
        return self.default() if value is None else value

    @classmethod
    def by_kind(cls, api_kind):
        return cls.map_by_api_kind.get(api_kind)

    @classmethod
    def by_meta(cls, meta):
        return cls.map_by_meta.get(meta)

    @classmethod
    def meta_defaults(cls):
        return {k: v.default() for k, v in cls.map_by_meta.items()}

    @classmethod
    def user_meta_from_api(cls, api_meta):
        user_meta = cls.meta_defaults()

        for k, v in {m["kind"]: m["metadata"] for m in api_meta}.items():
            if meta_object := cls.by_kind(k):
                meta_object.user_meta_from_api(user_meta, v)

        # remove 'None' metadata items
        for k, v in list(user_meta.items()):
            if v is None:
                del user_meta[k]

        return user_meta

    @classmethod
    def setters(cls, user_meta):
        res = []

        for meta, value in user_meta.items():
            if (m := cls.by_meta(meta)) and not m.immutable:
                res.append(
                    lambda api_zone_metadata_client, m=m, value=value: m.set(
                        m.value_or_default(value),
                        api_zone_metadata_client,
                    ),
                )

        return res

    @classmethod
    def updaters(cls, old_user_meta, new_user_meta):
        res = []

        for k, v in cls.map_by_meta.items():
            if not v.immutable:
                res.append(
                    lambda api_zone_metadata_client, k=k, v=v: v.update(
                        old_user_meta.get(k),
                        v.value_or_default(new_user_meta.get(k)),
                        api_zone_metadata_client,
                    ),
                )

        return res


class MetadataBinaryValue(Metadata):
    def default(self):
        return False

    def user_meta_from_api(self, user_meta, api_meta_item):
        user_meta[self.meta] = api_meta_item[0] == "1"

    def set(self, value, api_zone_metadata_client):
        if value:
            api_zone_metadata_client.modifyMetadata(
                metadata_kind=self.api_kind,
                metadata={"metadata": ["1"]},
            )

    def update(self, oldval, newval, api_zone_metadata_client):
        if newval == oldval:
            return False

        if newval:
            api_zone_metadata_client.modifyMetadata(
                metadata_kind=self.api_kind,
                metadata={"metadata": ["1"]},
            )
        else:
            api_zone_metadata_client.deleteMetadata(metadata_kind=self.api_kind)
        return True


class MetadataBinaryPresence(Metadata):
    def default(self):
        return False

    def user_meta_from_api(self, user_meta, _api_meta_item):
        user_meta[self.meta] = True

    def set(self, value, api_zone_metadata_client):
        if value:
            api_zone_metadata_client.modifyMetadata(
                metadata_kind=self.api_kind,
                metadata={"metadata": [""]},
            )

    def update(self, oldval, newval, api_zone_metadata_client):
        if newval == oldval:
            return False

        if newval:
            api_zone_metadata_client.modifyMetadata(
                metadata_kind=self.api_kind,
                metadata={"metadata": [""]},
            )
        else:
            api_zone_metadata_client.deleteMetadata(metadata_kind=self.api_kind)
        return True


class MetadataTernaryValue(Metadata):
    def default(self):
        return None

    def user_meta_from_api(self, user_meta, api_meta_item):
        user_meta[self.meta] = api_meta_item[0] == "1"

    def set(self, value, api_zone_metadata_client):
        if value is not None:
            if value:
                api_zone_metadata_client.modifyMetadata(
                    metadata_kind=self.api_kind,
                    metadata={"metadata": ["1"]},
                )
            else:
                api_zone_metadata_client.modifyMetadata(
                    metadata_kind=self.api_kind,
                    metadata={"metadata": ["0"]},
                )

    def update(self, oldval, newval, api_zone_metadata_client):
        if newval == oldval:
            return False

        if newval is not None:
            if newval:
                api_zone_metadata_client.modifyMetadata(
                    metadata_kind=self.api_kind,
                    metadata={"metadata": ["1"]},
                )
            else:
                api_zone_metadata_client.modifyMetadata(
                    metadata_kind=self.api_kind,
                    metadata={"metadata": ["0"]},
                )
        else:
            api_zone_metadata_client.deleteMetadata(metadata_kind=self.api_kind)
        return True


class MetadataListValue(Metadata):
    def default(self):
        return []

    def user_meta_from_api(self, user_meta, api_meta_item):
        user_meta[self.meta] = api_meta_item

    def set(self, value, api_zone_metadata_client):
        if len(value) != 0:
            api_zone_metadata_client.modifyMetadata(
                metadata_kind=self.api_kind,
                metadata={"metadata": value},
            )

    def update(self, oldval, newval, api_zone_metadata_client):
        if newval == oldval:
            return False

        if len(newval) != 0:
            api_zone_metadata_client.modifyMetadata(
                metadata_kind=self.api_kind,
                metadata={"metadata": newval},
            )
        else:
            api_zone_metadata_client.deleteMetadata(metadata_kind=self.api_kind)
        return True


class MetadataStringValue(Metadata):
    def default(self):
        return ""

    def user_meta_from_api(self, user_meta, api_meta_item):
        user_meta[self.meta] = api_meta_item[0]

    def set(self, value, api_zone_metadata_client):
        if value:
            api_zone_metadata_client.modifyMetadata(
                metadata_kind=self.api_kind,
                metadata={"metadata": [value]},
            )

    def update(self, oldval, newval, api_zone_metadata_client):
        if newval == oldval:
            return False

        if len(newval) != 0:
            api_zone_metadata_client.modifyMetadata(
                metadata_kind=self.api_kind,
                metadata={"metadata": [newval]},
            )
        else:
            api_zone_metadata_client.deleteMetadata(metadata_kind=self.api_kind)
        return True


class ZoneMetadata:
    map_by_zone_kind = {}
    map_by_meta = {}

    def __init__(self, api_kind, zone_kind):
        self.zone_kind = zone_kind
        self.meta = api_kind.lower().replace("-", "_")
        self.immutable = False
        self.map_by_zone_kind[self.zone_kind] = self
        self.map_by_meta[self.meta] = self

    def value_or_default(self, value):
        return self.default() if value is None else value

    @classmethod
    def by_kind(cls, zone_kind):
        return cls.map_by_zone_kind.get(zone_kind)

    @classmethod
    def by_meta(cls, meta):
        return cls.map_by_meta.get(meta)

    @classmethod
    def meta_defaults(cls):
        return {k: v.default() for k, v in cls.map_by_meta.items()}

    @classmethod
    def user_meta_from_api(cls, api_zone):
        user_meta = cls.meta_defaults()

        for k, v in api_zone.items():
            if meta_object := cls.by_kind(k):
                meta_object.user_meta_from_api(user_meta, v)

        return user_meta

    @classmethod
    def setters(cls, user_meta):
        res = []

        for meta, value in user_meta.items():
            if (m := cls.by_meta(meta)) and not m.immutable:
                res.append(
                    lambda zone_struct, m=m, value=value: m.set(
                        m.value_or_default(value),
                        zone_struct,
                    ),
                )

        return res

    @classmethod
    def updaters(cls, old_user_meta, new_user_meta):
        res = []

        for k, v in cls.map_by_meta.items():
            if not v.immutable:
                res.append(
                    lambda zone_struct, k=k, v=v: v.update(
                        old_user_meta.get(k),
                        v.value_or_default(new_user_meta.get(k)),
                        zone_struct,
                    ),
                )

        return res


class ZoneMetadataBinaryValue(ZoneMetadata):
    def default(self):
        return False

    def user_meta_from_api(self, user_meta, zone_meta_item):
        user_meta[self.meta] = zone_meta_item == "1"

    def set(self, value, zone_struct):
        if value:
            zone_struct[self.zone_kind] = "1"

    def update(self, oldval, newval, zone_struct):
        if newval != oldval:
            if newval:
                zone_struct[self.zone_kind] = "1"
            else:
                zone_struct[self.zone_kind] = "0"


class ZoneMetadataTernaryValue(ZoneMetadata):
    def default(self):
        return None

    def user_meta_from_api(self, user_meta, zone_meta_item):
        user_meta[self.meta] = zone_meta_item == "1"

    def set(self, value, zone_struct):
        if value is not None:
            if value:
                zone_struct[self.zone_kind] = "1"
            else:
                zone_struct[self.zone_kind] = "0"

    def update(self, oldval, newval, zone_struct):
        if newval != oldval:
            if newval is not None:
                if newval:
                    zone_struct[self.zone_kind] = "1"
                else:
                    zone_struct[self.zone_kind] = "0"
            else:
                zone_struct[self.zone_kind] = ""


class ZoneMetadataListValue(ZoneMetadata):
    def default(self):
        return []

    def user_meta_from_api(self, user_meta, zone_meta_item):
        user_meta[self.meta] = zone_meta_item

    def set(self, value, zone_struct):
        if value != []:
            zone_struct[self.zone_kind] = value

    def update(self, oldval, newval, zone_struct):
        if newval != oldval:
            zone_struct[self.zone_kind] = newval


class ZoneMetadataStringValue(ZoneMetadata):
    def default(self):
        return ""

    def user_meta_from_api(self, user_meta, zone_meta_item):
        user_meta[self.meta] = zone_meta_item

    def set(self, value, zone_struct):
        if value != "":
            zone_struct[self.zone_kind] = value

    def update(self, oldval, newval, zone_struct):
        if newval != oldval:
            zone_struct[self.zone_kind] = newval


MetadataListValue("ALLOW-DNSUPDATE-FROM")
MetadataListValue("ALLOW-AXFR-FROM")
MetadataListValue("ALSO-NOTIFY")
MetadataStringValue("AXFR-SOURCE")
MetadataBinaryPresence("FORWARD-DNSUPDATE")
MetadataStringValue("GSS-ACCEPTOR-PRINCIPAL")
MetadataStringValue("GSS-ALLOW-AXFR-PRINCIPAL")
MetadataBinaryValue("IXFR")
MetadataStringValue("LUA-AXFR-SCRIPT").immutable = True
MetadataBinaryValue("NOTIFY-DNSUPDATE")
MetadataBinaryValue("PUBLISH-CDNSKEY")
MetadataListValue("PUBLISH-CDS")
MetadataTernaryValue("SLAVE-RENOTIFY")
MetadataStringValue("SOA-EDIT-DNSUPDATE")
MetadataListValue("TSIG-ALLOW-DNSUPDATE")

ZoneMetadataBinaryValue("API-RECTIFY", "api_rectify")
ZoneMetadataListValue("AXFR-MASTER-TSIG", "slave_tsig_key_ids")
ZoneMetadataBinaryValue("NSEC3NARROW", "nsec3narrow")
ZoneMetadataStringValue("NSEC3PARAM", "nsec3param")
ZoneMetadataBinaryValue("PRESIGNED", "presigned").immutable = True
ZoneMetadataStringValue("SOA-EDIT", "soa_edit")
ZoneMetadataStringValue("SOA-EDIT-API", "soa_edit_api")
ZoneMetadataListValue("TSIG-ALLOW-AXFR", "master_tsig_key_ids")


def build_zone_result(api_zone_client, api_zone_metadata_client):
    api_zone = api_zone_client.listZone()
    api_meta = api_zone_metadata_client.listMetadata()
    z = {
        "exists": True,
        "name": api_zone["name"],
        "kind": api_zone["kind"],
        "serial": api_zone["serial"],
        "account": api_zone["account"],
        "dnssec": api_zone["dnssec"],
        "masters": api_zone["masters"],
        "metadata": {
            **Metadata.user_meta_from_api(api_meta),
            **ZoneMetadata.user_meta_from_api(api_zone),
        },
    }

    if "catalog" in api_zone:
        z["catalog"] = api_zone["catalog"]

    return api_zone, z


def main():
    module_args = {
        "state": {
            "type": "str",
            "default": "present",
            "choices": ["present", "absent", "exists", "notify", "retrieve"],
        },
        "name": {
            "type": "str",
            "required": True,
        },
        "server_id": {
            "type": "str",
            "default": "localhost",
        },
        "api_url": {
            "type": "str",
            "default": "http://localhost:8081",
        },
        "api_spec_path": {
            "type": "str",
            "default": "/api/docs",
        },
        "api_key": {
            "type": "str",
            "required": True,
            "no_log": True,
        },
        "properties": {
            "type": "dict",
            "options": {
                "kind": {
                    "type": "str",
                    "choices": ["Native", "Master", "Slave", "Producer", "Consumer"],
                    "required": True,
                },
                "account": {
                    "type": "str",
                },
                "catalog": {
                    "type": "str",
                },
                "nameservers": {
                    "type": "list",
                    "elements": "str",
                },
                "ttl": {
                    "type": "int",
                    "default": 86400,
                },
                "soa": {
                    "type": "dict",
                    "options": {
                        "mname": {
                            "type": "str",
                            "required": True,
                        },
                        "rname": {
                            "type": "str",
                            "required": True,
                        },
                        "serial": {
                            "type": "int",
                            "default": 1,
                        },
                        "refresh": {
                            "type": "int",
                            "default": 86400,
                        },
                        "retry": {
                            "type": "int",
                            "default": 7200,
                        },
                        "expire": {
                            "type": "int",
                            "default": 3600000,
                        },
                        "ttl": {
                            "type": "int",
                            "default": 172800,
                        },
                    },
                },
                "rrsets": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "name": {
                            "type": "str",
                            "required": True,
                        },
                        "type": {
                            "type": "str",
                            "required": True,
                        },
                        "ttl": {
                            "type": "int",
                            "default": 3600,
                        },
                        "records": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "disabled": {
                                    "type": "bool",
                                    "default": False,
                                },
                                "content": {
                                    "type": "str",
                                    "required": True,
                                },
                            },
                        },
                    },
                },
                "masters": {
                    "type": "list",
                    "elements": "str",
                },
                "master_tsig_key_ids": {
                    "type": "list",
                    "elements": "str",
                },
                "slave_tsig_key_ids": {
                    "type": "list",
                    "elements": "str",
                },
            },
        },
        "metadata": {
            "type": "dict",
            "options": {
                "allow_axfr_from": {
                    "type": "list",
                    "elements": "str",
                },
                "allow_dnsupdate_from": {
                    "type": "list",
                    "elements": "str",
                },
                "also_notify": {
                    "type": "list",
                    "elements": "str",
                },
                "api_rectify": {
                    "type": "bool",
                },
                "axfr_source": {
                    "type": "str",
                },
                "axfr_master_tsig": {
                    "type": "list",
                    "elements": "str",
                },
                "forward_dnsupdate": {
                    "type": "bool",
                },
                "gss_acceptor_principal": {
                    "type": "str",
                },
                "gss_allow_axfr_principal": {
                    "type": "str",
                },
                "ixfr": {
                    "type": "bool",
                },
                "notify_dnsupdate": {
                    "type": "bool",
                },
                "nsec3narrow": {
                    "type": "bool",
                },
                "nsec3param": {
                    "type": "str",
                },
                "publish_cdnskey": {
                    "type": "bool",
                },
                "publish_cds": {
                    "type": "list",
                    "elements": "str",
                },
                "slave_renotify": {
                    "type": "bool",
                },
                "soa_edit": {
                    "type": "str",
                    "choices": [
                        "INCREMENT-WEEKS",
                        "INCEPTION-EPOCH",
                        "INCEPTION-INCREMENT",
                        "EPOCH",
                        "NONE",
                    ],
                },
                "soa_edit_api": {
                    "type": "str",
                    "default": "DEFAULT",
                    "choices": [
                        "DEFAULT",
                        "INCREASE",
                        "EPOCH",
                        "SOA-EDIT",
                        "SOA-EDIT-INCREASE",
                    ],
                },
                "soa_edit_dnsupdate": {
                    "type": "str",
                    "default": "DEFAULT",
                    "choices": [
                        "DEFAULT",
                        "INCREASE",
                        "EPOCH",
                        "SOA-EDIT",
                        "SOA-EDIT-INCREASE",
                    ],
                },
                "tsig_allow_axfr": {
                    "type": "list",
                    "elements": "str",
                },
                "tsig_allow_dnsupdate": {
                    "type": "list",
                    "elements": "str",
                },
            },
        },
    }

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    result = {
        "changed": False,
    }

    state = module.params["state"]
    zone = module.params["name"]

    if module.check_mode:
        module.exit_json(**result)

    # create wrappers to proxy the raw API objects
    # and curry the server_id and zone_id into all API
    # calls automatically, along with handling
    # predictable exceptions
    api_zone_client = APIZoneWrapper(
        module=module, result=result, object_type="zones", zone_id=None
    )
    api_zone_metadata_client = APIZoneMetadataWrapper(
        module=module, result=result, object_type="zonemetadata", zone_id=None
    )

    result["zone"] = {}
    result["zone"]["name"] = zone
    result["zone"]["exists"] = False

    # first step is to get information about the zone, if it exists
    # this is required to translate the user-friendly zone name into
    # the zone_id required for subsequent API calls

    partial_zone_info = api_zone_client.listZones(zone=zone)

    if len(partial_zone_info) == 0:
        if state in ("exists", "absent"):
            # exit as there is nothing left to do
            module.exit_json(**result)
        elif state == "notify":
            module.fail_json(msg="NOTIFY cannot be requested for a non-existent zone", **result)
        elif state == "retrieve":
            module.fail_json(msg="Retrieval cannot be requested for a non-existent zone", **result)
        else:
            # state must be 'present'
            zone_id = None
    else:
        #
        # get the full zone info and populate the result dict
        zone_id = partial_zone_info[0]["id"]
        api_zone_client.zone_id = zone_id
        api_zone_metadata_client.zone_id = zone_id
        zone_info, result["zone"] = build_zone_result(api_zone_client, api_zone_metadata_client)

    # if only an existence check was requested,
    # the operation is complete
    if state == "exists":
        module.exit_json(**result)

    # if absence was requested, remove the zone and exit
    if state == "absent":
        api_zone_client.deleteZone()
        result["changed"] = True
        module.exit_json(**result)

    # if NOTIFY was requested, process it and exit
    if state == "notify":
        if zone_info["kind"] not in ["Master", "Producer"]:
            module.fail_json(
                msg=f"NOTIFY cannot be requested for '{zone_info['kind']}' zones",
                **result,
            )

        api_zone_client.notifyZone()
        result["changed"] = True
        module.exit_json(**result)

    # if retrieval was requested, process it and exit
    if state == "retrieve":
        if zone_info["kind"] not in ["Slave", "Consumer"]:
            module.fail_json(
                msg=f"Retrieval can only be requested for '{zone_info['kind']}' zones",
                **result,
            )

        api_zone_client.axfrRetrieveZone()
        result["changed"] = True
        module.exit_json(**result)

    # state must be 'present'
    if not zone_id:
        # create the requested zone
        zone_struct = {
            "name": zone,
        }

        if not module.params["properties"]:
            module.fail_json(msg="'properties' must be specified for zone creation", **result)

        props = module.params["properties"]

        zone_struct["kind"] = props["kind"]

        if props["kind"] in ["Native", "Master", "Producer"]:
            if not props["soa"]:
                module.fail_json(
                    msg=(
                        f"'properties -> soa' must be specified for '{props['kind']}' zone creation"
                    ),
                    **result,
                )

            if not props["nameservers"]:
                module.fail_json(
                    msg=(
                        f"'properties -> nameservers' must be specified for '{props['kind']}'"
                        " zone creation"
                    ),
                    **result,
                )

            # supply an empty nameserver list since NS records will be supplied in the rrsets
            zone_struct["nameservers"] = []

            zone_struct["rrsets"] = [
                {
                    "name": zone,
                    "type": "SOA",
                    "ttl": str(props["ttl"]),
                    "records": [
                        {
                            "disabled": False,
                            "content": " ".join(
                                [
                                    props["soa"]["mname"],
                                    props["soa"]["rname"],
                                    str(props["soa"]["serial"]),
                                    str(props["soa"]["refresh"]),
                                    str(props["soa"]["retry"]),
                                    str(props["soa"]["expire"]),
                                    str(props["soa"]["ttl"]),
                                ],
                            ),
                        },
                    ],
                },
                {
                    "name": zone,
                    "type": "NS",
                    "ttl": str(props["ttl"]),
                    "records": [{"disabled": False, "content": ns} for ns in props["nameservers"]],
                },
            ]

            if props["rrsets"]:
                for rrset in props["rrsets"]:
                    if rrset["type"] in ["SOA"]:
                        module.fail_json(
                            msg=(
                                f"'{rrset['type']}' type is not permitted in 'properties -> rrsets'"
                            ),
                            **result,
                        )
                        break
                    rrset["ttl"] = str(rrset["ttl"])
                    zone_struct["rrsets"].append(rrset)

        if props["kind"] in ["Slave", "Consumer"]:
            zone_struct["masters"] = props["masters"]

        if props["account"]:
            zone_struct["account"] = props["account"]

        if props["catalog"]:
            zone_struct["catalog"] = props["catalog"]

        if module.params["metadata"]:
            for setter in ZoneMetadata.setters(module.params["metadata"]):
                setter(zone_struct)

        partial_zone_info = api_zone_client.createZone(zone_struct=zone_struct)

        result["changed"] = True
        api_zone_client.zone_id = partial_zone_info["id"]
        api_zone_metadata_client.zone_id = partial_zone_info["id"]

        if module.params["metadata"]:
            for setter in Metadata.setters(module.params["metadata"]):
                setter(api_zone_metadata_client)

        zone_info, result["zone"] = build_zone_result(api_zone_client, api_zone_metadata_client)
    else:
        # compare the zone's attributes to the provided
        # options and update it if necessary
        zone_struct = {}

        if module.params["properties"]:
            props = module.params["properties"]

            if prop_kind := props["kind"]:
                if zone_info["kind"] != prop_kind:
                    zone_struct["kind"] = prop_kind

                if props["kind"] in ["Slave", "Consumer"] and props["masters"]:
                    mp_masters = sorted(props["masters"])
                    zi_masters = sorted(zone_info["masters"])

                    if zi_masters != mp_masters:
                        zone_struct["masters"] = props["masters"]

            if (prop_account := props["account"]) and zone_info["account"] != prop_account:
                zone_struct["account"] = prop_account

            if (prop_catalog := props["catalog"]) and zone_info["catalog"] != prop_catalog:
                zone_struct["catalog"] = prop_catalog

        if module.params["metadata"]:
            for updater in ZoneMetadata.updaters(
                result["zone"]["metadata"],
                module.params["metadata"],
            ):
                updater(zone_struct)

        if len(zone_struct):
            api_zone_client.putZone(zone_struct=zone_struct)
            result["changed"] = True

        if module.params["metadata"]:
            for updater in Metadata.updaters(result["zone"]["metadata"], module.params["metadata"]):
                if updater(api_zone_metadata_client):
                    result["changed"] = True

        if result["changed"]:
            zone_info, result["zone"] = build_zone_result(api_zone_client, api_zone_metadata_client)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
