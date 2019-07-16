# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

import uuid
from msrest.pipeline import ClientRawResponse

from .. import models


class UsageDetailsOperations(object):
    """UsageDetailsOperations operations.

    You should not instantiate directly this class, but create a Client instance that will create it for you and attach it as attribute.

    :param client: Client for service requests.
    :param config: Configuration of service client.
    :param serializer: An object model serializer.
    :param deserializer: An object model deserializer.
    :ivar api_version: Version of the API to be used with the client request. The current version is 2019-05-01. Constant value: "2019-05-01".
    """

    models = models

    def __init__(self, client, config, serializer, deserializer):

        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self.api_version = "2019-05-01"

        self.config = config

    def list(
            self, scope, expand=None, filter=None, skiptoken=None, top=None, metric=None, custom_headers=None, raw=False, **operation_config):
        """Lists the usage details for the defined scope. Usage details are
        available via this API only for May 1, 2014 or later.

        :param scope: The scope associated with usage details operations. This
         includes '/subscriptions/{subscriptionId}/' for subscription scope,
         '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}'
         for resourceGroup scope,
         '/providers/Microsoft.Billing/billingAccounts/{billingAccountId}' for
         Billing Account scope,
         '/providers/Microsoft.Billing/departments/{departmentId}' for
         Department scope,
         '/providers/Microsoft.Billing/enrollmentAccounts/{enrollmentAccountId}'
         for EnrollmentAccount scope and
         '/providers/Microsoft.Management/managementGroups/{managementGroupId}'
         for Management Group scope. For subscription, billing account,
         department, enrollment account and management group, you can also add
         billing period to the scope using
         '/providers/Microsoft.Billing/billingPeriods/{billingPeriodName}'. For
         e.g. to specify billing period at department scope use
         '/providers/Microsoft.Billing/departments/{departmentId}/providers/Microsoft.Billing/billingPeriods/{billingPeriodName}'
        :type scope: str
        :param expand: May be used to expand the properties/additionalInfo or
         properties/meterDetails within a list of usage details. By default,
         these fields are not included when listing usage details.
        :type expand: str
        :param filter: May be used to filter usageDetails by
         properties/resourceGroup, properties/resourceName,
         properties/resourceId, properties/chargeType,
         properties/reservationId, properties/publisherType or tags. The filter
         supports 'eq', 'lt', 'gt', 'le', 'ge', and 'and'. It does not
         currently support 'ne', 'or', or 'not'. Tag filter is a key value pair
         string where key and value is separated by a colon (:). PublisherType
         Filter accepts two values azure and marketplace and it is currently
         supported for Web Direct Offer Type
        :type filter: str
        :param skiptoken: Skiptoken is only used if a previous operation
         returned a partial result. If a previous response contains a nextLink
         element, the value of the nextLink element will include a skiptoken
         parameter that specifies a starting point to use for subsequent calls.
        :type skiptoken: str
        :param top: May be used to limit the number of results to the most
         recent N usageDetails.
        :type top: int
        :param metric: Allows to select different type of cost/usage records.
         Possible values include: 'ActualCostMetricType',
         'AmortizedCostMetricType', 'UsageMetricType'
        :type metric: str or ~azure.mgmt.consumption.models.Metrictype
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: An iterator like instance of UsageDetail
        :rtype:
         ~azure.mgmt.consumption.models.UsageDetailPaged[~azure.mgmt.consumption.models.UsageDetail]
        :raises:
         :class:`ErrorResponseException<azure.mgmt.consumption.models.ErrorResponseException>`
        """
        def prepare_request(next_link=None):
            if not next_link:
                # Construct URL
                url = self.list.metadata['url']
                path_format_arguments = {
                    'scope': self._serialize.url("scope", scope, 'str', skip_quote=True)
                }
                url = self._client.format_url(url, **path_format_arguments)

                # Construct parameters
                query_parameters = {}
                if expand is not None:
                    query_parameters['$expand'] = self._serialize.query("expand", expand, 'str')
                if filter is not None:
                    query_parameters['$filter'] = self._serialize.query("filter", filter, 'str')
                if skiptoken is not None:
                    query_parameters['$skiptoken'] = self._serialize.query("skiptoken", skiptoken, 'str')
                if top is not None:
                    query_parameters['$top'] = self._serialize.query("top", top, 'int', maximum=1000, minimum=1)
                query_parameters['api-version'] = self._serialize.query("self.api_version", self.api_version, 'str')
                if metric is not None:
                    query_parameters['metric'] = self._serialize.query("metric", metric, 'str')

            else:
                url = next_link
                query_parameters = {}

            # Construct headers
            header_parameters = {}
            header_parameters['Accept'] = 'application/json'
            if self.config.generate_client_request_id:
                header_parameters['x-ms-client-request-id'] = str(uuid.uuid1())
            if custom_headers:
                header_parameters.update(custom_headers)
            if self.config.accept_language is not None:
                header_parameters['accept-language'] = self._serialize.header("self.config.accept_language", self.config.accept_language, 'str')

            # Construct and send request
            request = self._client.get(url, query_parameters, header_parameters)
            return request

        def internal_paging(next_link=None):
            request = prepare_request(next_link)

            response = self._client.send(request, stream=False, **operation_config)

            if response.status_code not in [200]:
                raise models.ErrorResponseException(self._deserialize, response)

            return response

        # Deserialize response
        header_dict = None
        if raw:
            header_dict = {}
        deserialized = models.UsageDetailPaged(internal_paging, self._deserialize.dependencies, header_dict)

        return deserialized
    list.metadata = {'url': '/{scope}/providers/Microsoft.Consumption/usageDetails'}
