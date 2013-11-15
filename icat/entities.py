"""Provide the classes corresponding to the entities in the ICAT schema.

Entity classes defined in this module are derived from the abstract
base class `Entity` from module `icat.entity`.  They override the
class variables ``BeanName``, ``InstAttr``, ``InstRel``, and
``InstMRel`` as appropriate.
"""

from icat.entity import Entity


class Parameter(Entity):
    """Abstract base class for ``DatafileParameter``,
    ``DatasetParameter``, ``InvestigationParameter``,
    ``SampleParameter``, and ``DataCollectionParameter``."""
    InstAttr = frozenset(['id', 'numericValue', 'dateTimeValue', 'stringValue', 
                          'rangeBottom', 'rangeTop', 'error'])
    InstRel = frozenset(['type'])


class Application(Entity):
    """Some piece of software."""
    BeanName = 'Application'
    InstAttr = frozenset(['id', 'name', 'version'])
    InstMRel = frozenset(['jobs'])


class Application43(Application):
    """Some piece of software.  Valid for ICAT 4.3.*."""
    InstRel = frozenset(['facility'])


class DataCollection(Entity):
    """A set of Datafiles and Datasets which can span investigations
    and facilities.  Note that it has no constraint fields.  It is
    expected that a DataCollection would be identified by its
    DataCollectionParameters or its relationship to a Job."""
    BeanName = 'DataCollection'
    InstMRel = frozenset(['dataCollectionDatafiles', 'dataCollectionDatasets', 
                          'dataCollectionParameters', 'jobsAsInput', 
                          'jobsAsOutput'])


class DataCollectionDatafile(Entity):
    """Represents a many-to-many relationship between a DataCollection
    and its Datafiles."""
    BeanName = 'DataCollectionDatafile'
    InstRel = frozenset(['dataCollection', 'datafile'])


class DataCollectionDataset(Entity):
    """Represents a many-to-many relationship between a DataCollection
    and its datasets."""
    BeanName = 'DataCollectionDataset'
    InstRel = frozenset(['dataCollection', 'dataset'])


class DataCollectionParameter(Parameter):
    """A parameter associated with a DataCollection."""
    BeanName = 'DataCollectionParameter'
    InstRel = frozenset(['dataCollection', 'type'])


class Datafile(Entity):
    """A data file."""
    BeanName = 'Datafile'
    InstAttr = frozenset(['id', 'name', 'description', 'location', 'fileSize', 
                          'checksum', 'datafileCreateTime', 'datafileModTime', 
                          'doi'])
    InstRel = frozenset(['datafileFormat', 'dataset'])
    InstMRel = frozenset(['parameters', 'inputDatafiles', 'outputDatafiles', 
                          'sourceDatafiles', 'destDatafiles'])


class Datafile43(Datafile):
    """A data file.  Valid for ICAT 4.3.*."""
    InstMRel = frozenset(['parameters', 'dataCollectionDatafiles', 
                          'sourceDatafiles', 'destDatafiles'])


class DatafileFormat(Entity):
    """A data file format."""
    BeanName = 'DatafileFormat'
    InstAttr = frozenset(['id', 'name', 'description', 'version', 'type'])
    InstRel = frozenset(['facility'])
    InstMRel = frozenset(['datafiles'])


class DatafileParameter(Parameter):
    """A parameter associated with a data file."""
    BeanName = 'DatafileParameter'
    InstRel = frozenset(['datafile', 'type'])


class Dataset(Entity):
    """A collection of data files and part of an investigation."""
    BeanName = 'Dataset'
    InstAttr = frozenset(['id', 'name', 'description', 'location', 
                          'startDate', 'endDate', 'complete', 'doi'])
    InstRel = frozenset(['type', 'sample', 'investigation'])
    InstMRel = frozenset(['parameters', 'datafiles', 
                          'inputDatasets', 'outputDatasets'])


class Dataset43(Dataset):
    """A collection of data files and part of an investigation.  Valid
    for ICAT 4.3.*."""
    InstMRel = frozenset(['parameters', 'datafiles', 'dataCollectionDatasets'])


class DatasetParameter(Parameter):
    """A parameter associated with a data set."""
    BeanName = 'DatasetParameter'
    InstRel = frozenset(['dataset', 'type'])


class DatasetType(Entity):
    """A type of data set."""
    BeanName = 'DatasetType'
    InstAttr = frozenset(['id', 'name', 'description'])
    InstRel = frozenset(['facility'])
    InstMRel = frozenset(['datasets'])


class Facility(Entity):
    """An experimental facility."""
    BeanName = 'Facility'
    InstAttr = frozenset(['id', 'name', 'fullName', 'description', 'url', 
                          'daysUntilRelease'])
    InstMRel = frozenset(['instruments', 'facilityCycles', 'investigations', 
                          'parameterTypes', 'datafileFormats', 'datasetTypes', 
                          'sampleTypes', 'investigationTypes'])


class Facility43(Facility):
    """An experimental facility.  Valid for ICAT 4.3.*."""
    InstMRel = frozenset(['instruments', 'facilityCycles', 'investigations', 
                          'parameterTypes', 'datafileFormats', 'datasetTypes', 
                          'sampleTypes', 'investigationTypes', 'applications'])


class FacilityCycle(Entity):
    """An operating cycle within a facility"""
    BeanName = 'FacilityCycle'
    InstAttr = frozenset(['id', 'name', 'description', 'startDate', 'endDate'])
    InstRel = frozenset(['facility'])
    InstMRel = frozenset(['investigations'])


class FacilityCycle43(FacilityCycle):
    """An operating cycle within a facility.  Valid for ICAT 4.3.*."""
    InstMRel = frozenset([])


class Group(Entity):
    """A group of users."""
    BeanName = 'Group'
    InstAttr = frozenset(['id', 'name'])
    InstMRel = frozenset(['userGroups', 'rules'])

    def addUser(self, users):
        ugs = []
        uids = set()
        for u in users:
            if u.id in uids:
                continue
            if self.client.apiversion < '4.3':
                ugs.append(self.client.new('userGroup', user=u, group=self))
            else:
                ugs.append(self.client.new('userGroup', user=u, grouping=self))
            uids.add(u.id)
        self.client.createMany(ugs)


class Group43(Group):
    """A group of users.  Valid for ICAT 4.3.*."""
    BeanName = 'Grouping'


class InputDatafile(Entity):
    """Many to many relationship between data file as input and a job."""
    BeanName = 'InputDatafile'
    InstRel = frozenset(['job', 'datafile'])


class InputDataset(Entity):
    """Many to many relationship between data set as input and a job."""
    BeanName = 'InputDataset'
    InstRel = frozenset(['job', 'dataset'])


class Instrument(Entity):
    """Used by a user within an investigation."""
    BeanName = 'Instrument'
    InstAttr = frozenset(['id', 'name', 'fullName', 'description', 'type'])
    InstRel = frozenset(['facility'])
    InstMRel = frozenset(['instrumentScientists', 'investigations'])

    def addInstrumentScientist(self, name, search=False, **kwargs):
        user = self.client.createUser(name, search, **kwargs)
        instsci = self.client.new('instrumentScientist', 
                                  instrument=self, user=user)
        instsci.create()
        return user


class Instrument43(Instrument):
    """Used by a user within an investigation.  Valid for ICAT 4.3.*."""
    InstAttr = frozenset(['id', 'name', 'fullName', 'description', 'type', 
                          'url'])
    InstMRel = frozenset(['instrumentScientists', 'investigationInstruments'])


class InstrumentScientist(Entity):
    """Relationship between an ICAT user as an instrument scientist
    and the instrument."""
    BeanName = 'InstrumentScientist'
    InstRel = frozenset(['user', 'instrument'])


class Investigation(Entity):
    """An investigation or experiment."""
    BeanName = 'Investigation'
    InstAttr = frozenset(['id', 'name', 'title', 'summary', 'doi', 'visitId', 
                          'startDate', 'endDate', 'releaseDate'])
    InstRel = frozenset(['type', 'facility', 'instrument', 'facilityCycle'])
    InstMRel = frozenset(['parameters', 'investigationUsers', 'keywords', 
                          'publications', 'samples', 'datasets', 'shifts', 
                          'studyInvestigations'])

    def addInstrument(self, instrument):
        self.get()
        self.instrument = instrument
        self.update()

    def addKeywords(self, keywords):
        kws = []
        for k in keywords:
            kws.append(self.client.new('keyword', name=k, investigation=self))
        self.client.createMany(kws)

    def addInvestigationUser(self, name, role='Investigator', search=False, 
                             **kwargs):
        user = self.client.createUser(name, search, **kwargs)
        iu = self.client.new('investigationUser', 
                             investigation=self, user=user, role=role)
        iu.create()
        return user


class Investigation43(Investigation):
    """An investigation or experiment.  Valid for ICAT 4.3.*."""
    InstRel = frozenset(['type', 'facility'])
    InstMRel = frozenset(['parameters', 'investigationInstruments', 
                          'investigationUsers', 'keywords', 
                          'publications', 'samples', 'datasets', 'shifts', 
                          'studyInvestigations'])

    def addInstrument(self, instrument):
        ii = self.client.new('investigationInstrument', 
                             investigation=self, instrument=instrument)
        ii.create()


class InvestigationInstrument(Entity):
    """Represents a many-to-many relationship between an investigation
    and the instruments assigned."""
    BeanName = 'InvestigationInstrument'
    InstRel = frozenset(['investigation', 'instrument'])


class InvestigationParameter(Parameter):
    """A parameter associated with an investigation."""
    BeanName = 'InvestigationParameter'
    InstRel = frozenset(['investigation', 'type'])


class InvestigationType(Entity):
    """A type of investigation."""
    BeanName = 'InvestigationType'
    InstAttr = frozenset(['id', 'name', 'description'])
    InstRel = frozenset(['facility'])
    InstMRel = frozenset(['investigations'])


class InvestigationUser(Entity):
    """Many to many relationship between investigation and user."""
    BeanName = 'InvestigationUser'
    InstAttr = frozenset(['id', 'role'])
    InstRel = frozenset(['user', 'investigation'])


class Job(Entity):
    """A run of an application with its related inputs and outputs."""
    BeanName = 'Job'
    InstRel = frozenset(['application'])
    InstMRel = frozenset(['inputDatafiles', 'inputDatasets', 
                          'outputDatafiles', 'outputDatasets'])


class Job43(Job):
    """A run of an application with its related inputs and outputs.
    Valid for ICAT 4.3.*."""
    InstAttr = frozenset(['id', 'arguments'])
    InstRel = frozenset(['application', 'inputDataCollection', 
                         'outputDataCollection'])
    InstMRel = frozenset([])


class Keyword(Entity):
    """A Keyword related to an investigation."""
    BeanName = 'Keyword'
    InstAttr = frozenset(['id', 'name'])
    InstRel = frozenset(['investigation'])


class NotificationRequest(Entity):
    """Registers a request for a JMS notification to be sent out."""
    BeanName = 'NotificationRequest'
    InstAttr = frozenset(['id', 'name', 'what', 'crudFlags', 'datatypes', 
                          'destType', 'jmsOptions'])


class Log(Entity):
    """To store call logs if configured in icat.properties."""
    BeanName = 'Log'
    InstAttr = frozenset(['id', 'query', 'operation', 'entityId', 'entityName', 
                          'duration'])


class OutputDatafile(Entity):
    """Many to many relationship between data file as output and a job."""
    BeanName = 'OutputDatafile'
    InstRel = frozenset(['job', 'datafile'])


class OutputDataset(Entity):
    """Many to many relationship between data set as output and a job."""
    BeanName = 'OutputDataset'
    InstRel = frozenset(['job', 'dataset'])


class ParameterType(Entity):
    """A parameter type with unique name and units."""
    BeanName = 'ParameterType'
    InstAttr = frozenset(['id', 'name', 'description', 'valueType', 'units', 
                          'unitsFullName', 'minimumNumericValue', 
                          'maximumNumericValue', 'enforced', 'verified', 
                          'applicableToDatafile', 'applicableToDataset', 
                          'applicableToSample', 'applicableToInvestigation'])
    InstRel = frozenset(['facility'])
    InstMRel = frozenset(['datafileParameters', 'datasetParameters', 
                          'sampleParameters', 'investigationParameters', 
                          'permissibleStringValues'])


class ParameterType43(ParameterType):
    """A parameter type with unique name and units.  Valid for ICAT 4.3.*."""
    InstAttr = frozenset(['id', 'name', 'description', 'valueType', 'units', 
                          'unitsFullName', 'minimumNumericValue', 
                          'maximumNumericValue', 'enforced', 'verified', 
                          'applicableToDatafile', 'applicableToDataset', 
                          'applicableToSample', 'applicableToInvestigation', 
                          'applicableToDataCollection'])
    InstMRel = frozenset(['datafileParameters', 'datasetParameters', 
                          'sampleParameters', 'investigationParameters', 
                          'dataCollectionParameters', 
                          'permissibleStringValues'])


class PermissibleStringValue(Entity):
    """Permissible value for string parameter types."""
    BeanName = 'PermissibleStringValue'
    InstAttr = frozenset(['id', 'value'])
    InstRel = frozenset(['type'])


class PublicStep(Entity):
    """An allowed step for an INCLUDE identifed by the origin entity
    and the field name for navigation.  Including an entry here is
    much more efficient than having to use the authorization rules."""
    BeanName = 'PublicStep'
    InstAttr = frozenset(['id', 'origin', 'field'])


class Publication(Entity):
    """A publication."""
    BeanName = 'Publication'
    InstAttr = frozenset(['id', 'fullReference', 'url', 'doi', 'repository', 
                          'repositoryId'])
    InstRel = frozenset(['investigation'])


class RelatedDatafile(Entity):
    """Used to represent an arbitrary relationship between data files."""
    BeanName = 'RelatedDatafile'
    InstAttr = frozenset(['id', 'relation'])
    InstRel = frozenset(['sourceDatafile', 'destDatafile'])


class Rule(Entity):
    """An authorization rule."""
    BeanName = 'Rule'
    InstAttr = frozenset(['id', 'what', 'crudFlags'])
    InstRel = frozenset(['group'])


class Rule43(Rule):
    """An authorization rule.  Valid for ICAT 4.3.*."""
    InstRel = frozenset(['grouping'])


class Sample(Entity):
    """A sample to be used in an investigation."""
    BeanName = 'Sample'
    InstAttr = frozenset(['id', 'name'])
    InstRel = frozenset(['type', 'investigation'])
    InstMRel = frozenset(['parameters', 'datasets'])


class SampleParameter(Parameter):
    """A parameter associated with a sample."""
    BeanName = 'SampleParameter'
    InstRel = frozenset(['sample', 'type'])


class SampleType(Entity):
    """A sample to be used in an investigation."""
    BeanName = 'SampleType'
    InstAttr = frozenset(['id', 'name', 'molecularFormula', 
                          'safetyInformation'])
    InstRel = frozenset(['facility'])
    InstMRel = frozenset(['samples'])


class Shift(Entity):
    """A period of time related to an investigation."""
    BeanName = 'Shift'
    InstAttr = frozenset(['id', 'comment', 'startDate', 'endDate'])
    InstRel = frozenset(['investigation'])


class Study(Entity):
    """A study which may be related to an investigation."""
    BeanName = 'Study'
    InstAttr = frozenset(['id', 'name', 'description', 'status', 'startDate'])
    InstRel = frozenset(['user'])
    InstMRel = frozenset(['studyInvestigations'])


class StudyInvestigation(Entity):
    """Many to many relationship between study and investigation."""
    BeanName = 'StudyInvestigation'
    InstRel = frozenset(['study', 'investigation'])


class User(Entity):
    """A user of the facility."""
    BeanName = 'User'
    InstAttr = frozenset(['id', 'name', 'fullName'])
    InstMRel = frozenset(['investigationUsers', 'instrumentScientists', 
                          'userGroups', 'studies'])


class UserGroup(Entity):
    """Many to many relationship between user and group."""
    BeanName = 'UserGroup'
    InstRel = frozenset(['user', 'group'])


class UserGroup43(UserGroup):
    """Many to many relationship between user and group.  Valid for
    ICAT 4.3.*."""
    InstRel = frozenset(['user', 'grouping'])


