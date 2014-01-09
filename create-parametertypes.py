#! /usr/bin/python
#
# Create some parameter types, (actually just one for testing atm).
#

import icat
import icat.config
import sys
import logging

logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)

icat.config.defaultsection = "hzb"
conf = icat.config.Config().getconfig()

client = icat.Client(conf.url, **conf.client_kwargs)
client.login(conf.auth, conf.credentials)


# ------------------------------------------------------------
# Some parameter type data
# ------------------------------------------------------------

parametertype_data = [
    {
        'name': "temperature",
        'units': "K",
        'unitsFullName': "kelvin",
        'valueType': "NUMERIC",
    },
]


# ------------------------------------------------------------
# Get some objects from ICAT we need later on
# ------------------------------------------------------------

hzb = client.assertedSearch("Facility[name='HZB']")[0]

# ------------------------------------------------------------
# Create the sample type
# ------------------------------------------------------------

parametertypes = []
for pdata in parametertype_data:
    print "ParameterType: creating '%s' ..." % pdata['name']
    parametertype = client.new("parameterType")
    parametertype.name = pdata['name']
    parametertype.units = pdata['units']
    parametertype.unitsFullName = pdata['unitsFullName']
    parametertype.valueType = pdata['valueType']
    parametertype.applicableToDatafile = True
    parametertype.applicableToDataset = True
    parametertype.applicableToSample = True
    parametertype.applicableToInvestigation = True
    parametertype.facility = hzb
    parametertypes.append(parametertype)
client.createMany(parametertypes)

