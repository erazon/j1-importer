import datetime

import mongoengine
from models.courseprovider.course_provider import CourseProvider
from models.courseprovider.instructor import Instructor
from models.courseprovider.provider_site import CourseProviderSite
from models.importer import BaseImporterConfig
from models.importer.base import ImporterStatus
from models.importer.higher_reach import HigherReachImporterConfig
from mongoengine import DoesNotExist

from config import Config


def mongodb_connection():
    mongoengine.connect(
        db=Config.MONGODB_DATABASE,
        host=Config.MONGODB_HOST,
        port=Config.MONGODB_PORT,
        username=Config.MONGODB_USERNAME,
        password=Config.MONGODB_PASSWORD,
        authentication_source=Config.MONGODB_AUTH_DATABASE
    )


def get_importer():
    _id = "5e106afbe4a962b983bfed1f"
    try:
        ins = BaseImporterConfig.objects(id=_id).get()
        return ins
    except DoesNotExist:
        print('does not exists')
    return None


def get_course_provider_site(name=None):
    return CourseProviderSite.objects(name=name)


def get_course_provider(_id=None):
    return CourseProvider.objects.get(id=_id)


def get_Instractor():
    name = "instractor_name_03"
    external_id = "12345"
    try:
        ins = Instructor.objects(name=name, external_id=external_id).get()
        print(ins.id)
    except DoesNotExist:
        print('does not exists')
        pass
    # print(ins.to_json())


def create_course_provider(base_url, code):
    name = "MyName"
    summary = "My summary"
    description = "My description"

    course_provider = CourseProvider(
        name=name,
        logo={},
        code=code,
        summary=summary,
        description=description,
        created_at=datetime.datetime.now(),
        created_by="Importer-Name: " + "HigherReach"
    )
    course_provider.save()
    print("CourseProvider: ", course_provider.to_json(indent=2))
    return course_provider


def create_importer(base_urls=None):
    for base_url in base_urls:
        provider = create_course_provider(base_url[0], base_url[1])
        importer_config = HigherReachImporterConfig(
            base_url=base_url[0],
            course_provider=provider,
            name="HigherReach",
            code=base_url[1],
            status=ImporterStatus.READY.value,
            cron_rule="cron_rule",
            next_exec_time=datetime.datetime.utcnow()
        )
        importer_config.save(force_insert=True)

        print("Provider-ID: ", provider.id)
        print("Code: {} | Importer-ID: {}".format(
            base_url[1], importer_config.id))


def main():
    mongodb_connection()
    base_urls = [
        ("http://gateway1.dev.campusops.net/modules/shop", "JZ Demo"),
        ("https://register.graduateschool.edu/modules/shop", "GSD"),
        ("https://noncredit.its.sfu.ca/modules/shop", "SFU"),
        ("https://nts.drexel.edu/modules/shop", "Drexel"),
        ("https://register.ece.emory.edu/modules/shop", "Emory"),
        ("https://school.icp.org/modules/shop", "ICP"),
        ("http://reg.outreach.lsu.edu/modules/shop", "LSU"),
        ("https://pdlearn.nnu.edu/modules/shop", "Northwest Nazarere"),
        ("https://sdc.admin.campusops.net/modules/shop", "SDSU"),
        ("https://higherreach.csusm.edu/modules/shop", "CSUSM"),
        ("https://course.ucsc-extension.edu/modules/shop", "UCSC"),
        ("http://higherreach.polk.edu/modules/shop", "Polk state"),
        ("http://learn.mhcc.edu/modules/shop", "Mt Hood")
    ]

    # importerconfig
    create_importer(base_urls)


if __name__ == '__main__':
    main()
