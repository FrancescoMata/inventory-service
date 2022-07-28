
from importlib.metadata import metadata
from numpy import number

from sqlalchemy import Table, MetaData, create_engine, select

from fastapi import APIRouter
from dotenv import load_dotenv
from pydantic import BaseModel
import pandas as pd
from fastapi.responses import FileResponse
engine = create_engine("postgresql://postgres:admin@localhost/mobi1")


metadata = MetaData(bind=None)
devices = Table(
    'devices',
    metadata,
    autoload=True,
    autoload_with=engine

)

devicesManufacturersLinks = Table(
    'devices_manufacturer_links',
    metadata,
    autoload=True,
    autoload_with=engine

)

manufacturers = Table(
    'manufacturers',
    metadata,
    autoload=True,
    autoload_with=engine

)

capacity = Table(
    'capacities',
    metadata,
    autoload=True,
    autoload_with=engine

)

network = Table(
    'networks',
    metadata,
    autoload=True,
    autoload_with=engine

)

grade = Table(
    'grades',
    metadata,
    autoload=True,
    autoload_with=engine

)

pricingDevices = Table(
    'device_prices_device_links',
    metadata,
    autoload=True,
    autoload_with=engine

)

pricingDeviceNetwork = Table(
    'device_prices_network_links',
    metadata,
    autoload=True,
    autoload_with=engine
)

pricingDeviceCapacity = Table(
    'device_prices_capacity_links',
    metadata,
    autoload=True,
    autoload_with=engine
)

pricingDeviceGrades = Table(
    'device_prices_grade_links',
    metadata,
    autoload=True,
    autoload_with=engine
)


class Item(BaseModel):
    id: str
    value: str


class Message(BaseModel):
    message: str


router = APIRouter()

load_dotenv('.env')

connection = engine.connect()
# to avoid csrftokenError
# router.add_middleware(DBSessionMiddleware, db_url=os.environ['POSTGRES_URI'])


@router.get("/gbt/generate-pricing-comparison-site")
async def build_csv():
    pricingCSV = getPricingCSV()
    pricingDevice = getPricingFromDB()
    pricingCapacity = getPricingDeviceCapacity()
    pricingNetwork = getPricingNetworkFromDB()
    pricingGrade = getPricingDeviceGrades()

    mapDevices = pd.merge(pricingDevice,
                          pricingCapacity, left_on="device_price_id", right_on="device_price_id", how="right")

    mapDevicesNetwork = pd.merge(mapDevices,
                                 pricingNetwork, left_on="device_price_id", right_on="device_price_id", how="right")

    mapDevicesGrades = pd.merge(mapDevicesNetwork,
                                pricingGrade, left_on="device_price_id", right_on="device_price_id", how="right")

    filterPricingCSV = pricingCSV.loc[(
        pricingCSV['network'] == 'Unlocked')]
    filterPricingCSV['capacity'] = filterPricingCSV['capacity'].astype(
        str)
    print(filterPricingCSV)
    filterNetworks = mapDevicesGrades.loc[(
        mapDevicesGrades['network_id'] == 3)]

    filterNetworks['network_id'] = filterNetworks['network_id'].astype(
        str)
    filterNetworks['network_id'] = filterNetworks['network_id'].str.replace(
        '3', 'Unlocked')

    filterNetworks['network_id']
    filterNetworks = filterNetworks.loc[(
        filterNetworks['grade_id'] == 7)]

    filterNetworks['capacity_id'] = filterNetworks['capacity_id'].astype(
        str)
    filterNetworks['capacity_id'] = filterNetworks['capacity_id'].str.replace(
        '12', '1')
    filterNetworks['capacity_id'] = filterNetworks['capacity_id'].str.replace(
        '16', '64')
    filterNetworks['capacity_id'] = filterNetworks['capacity_id'].str.replace(
        '18', '512')
    filterNetworks['capacity_id'] = filterNetworks['capacity_id'].str.replace(
        '14', '32')
    filterNetworks['capacity_id'] = filterNetworks['capacity_id'].str.replace(
        '17', '256')
    filterNetworks['capacity_id'] = filterNetworks['capacity_id'].str.replace(
        '19', '2')
    filterNetworks['capacity_id'] = filterNetworks['capacity_id'].str.replace(
        '15', '16')
    filterNetworks['capacity_id'] = filterNetworks['capacity_id'].str.replace(
        '13', '128')

    mapDevicesCSV = pd.merge(filterPricingCSV,
                             filterNetworks, left_on=["id", "capacity", "network"], right_on=["device_id", "capacity_id", "network_id"], how="left")

    mapDevicesCSV['device_price_id'] = mapDevicesCSV['device_price_id'].astype(
        str)

    mapDevicesCSV['capacity'] = mapDevicesCSV['capacity'].astype(
        int)
    mapDevicesCSV['unit'] = mapDevicesCSV['capacity'].apply(
        lambda x: 'To' if x <= 2 else "Go")

    mapDevicesCSV["capacity"] = mapDevicesCSV['capacity'].astype(
        str) + mapDevicesCSV["unit"]

    prepareCSVForStrapi = pd.DataFrame({
        "Marque": mapDevicesCSV['manufacturer'],
        "Modele": mapDevicesCSV['name'],
        "Prix Comme neuf": (mapDevicesCSV['grade_b'].apply(lambda x: (x * 1.175))).astype(int),
        "Prix tres bon etat": (mapDevicesCSV['grade_b'].apply(lambda x: (x * 1.175))).astype(int),
        "Prix marque/raye": (mapDevicesCSV['grade_c'].apply(lambda x: (x * 1.175))).astype(int),
        "Prix ecran casse": (mapDevicesCSV['grade_d'].apply(lambda x: (x * 1.175))).astype(int),
        "URL landing page produit": ('https://goodbuytech-fr.twigcard.com/devices/' + mapDevicesCSV['manufacturer'] + '-' + mapDevicesCSV['name'] + '-' + mapDevicesCSV['capacity'] + '-' + mapDevicesCSV['device_price_id']),
        "Capacite": mapDevicesCSV['capacity']
    })

    prepareCSVForStrapi.to_csv('gbt-data/pricing-comparison-site.csv')
    return FileResponse('gbt-data/pricing-comparison-site.csv', media_type='application/octet-stream', filename='comparison-site.csv')


@router.get("/gbt/generate-pricing-strapi")
async def read_item():
    pricingCSV = getPricingCSV()
    manufacturersData = getManufacturers()
    manufacturersData.columns = 'manufacturers_' + manufacturersData.columns.values
    mapPricingManufacturers = pd.merge(pricingCSV,
                                       manufacturersData, left_on="manufacturer", right_on="manufacturers_name", how="left").reset_index(drop=True)

    mapPricingManufacturers['grade'] = mapPricingManufacturers.apply(lambda x: [
        ('Grade B', x['grade_b']), ('Grade C', x['grade_c']), ('Grade D', x['grade_d']), ('Grade E', x['grade_e'])], axis=1)
    mapPricingManufacturers = mapPricingManufacturers.explode(
        'grade').reset_index(drop=True)
    mapPricingManufacturers[['grade', 'price_gbp']
                            ] = pd.DataFrame(mapPricingManufacturers['grade'].tolist())

    capacityData = getCapacity()
    capacityData.columns = 'capacity_' + capacityData.columns.values
    print(capacityData)
    mapPricingManufacturers['capacity'] = mapPricingManufacturers['capacity'].astype(
        str)
    mapPricingCapacity = pd.merge(mapPricingManufacturers,
                                  capacityData, left_on="capacity", right_on="capacity_capacity", how="left").reset_index(drop=True)

    gradesData = getGrade()
    gradesData.columns = 'grade_' + gradesData.columns.values
    mapGradesData = pd.merge(mapPricingCapacity,
                             gradesData, left_on="grade", right_on="grade_grade", how="left").reset_index(drop=True)
    filterGradesData = mapGradesData.loc[(
        mapGradesData['grade_locale'] == 'fr')]

    networkData = getNetwork()
    networkData.columns = 'network_' + networkData.columns.values
    mapNetworkData = pd.merge(filterGradesData,
                              networkData, left_on="network", right_on="network_name", how="left").drop_duplicates()

    prepareCSVForStrapi = pd.DataFrame({
        "device": mapNetworkData['id'],
        "manufacturer": mapNetworkData['manufacturers_id'],
        "capacity": mapNetworkData['capacity_id'].astype(str).apply(lambda x: x.replace('.0', '')),
        "network": mapNetworkData['network_id'],
        "grade": mapNetworkData['grade_id'],
        "price_gbp": mapNetworkData['price_gbp'],
        "price_eur": mapNetworkData['price_gbp'].apply(lambda x: (x * 1.175)),
        "price_usd": mapNetworkData['price_gbp'].apply(lambda x: (x * 1.200)),
        "publishedAt": "2022-06-17T18:11:17.382Z"
    })
    prepareCSVForStrapi.to_csv('gbt-data/new_pricing.csv', index=False)
    return FileResponse('gbt-data/new_pricing.csv', media_type='application/octet-stream', filename='new_pricing.csv')


def getCapacity():
    capacitySelect = select([
        capacity.columns.id,
        capacity.columns.capacity

    ])
    resultCapacities = connection.execute(capacitySelect).fetchall()
    dfCapacities = pd.DataFrame(resultCapacities)
    dfCapacities.columns = ["id", "capacity"]
    return dfCapacities


def getNetwork():
    networkSelect = select([
        network.columns.id,
        network.columns.name

    ])
    resultNetworks = connection.execute(networkSelect).fetchall()
    dfNetworks = pd.DataFrame(resultNetworks)
    dfNetworks.columns = ["id", "name"]
    return dfNetworks


def getGrade():
    gradeSelect = select([
        grade.columns.id,
        grade.columns.grade,
        grade.columns.locale

    ])
    resultGrades = connection.execute(gradeSelect).fetchall()
    dfGrades = pd.DataFrame(resultGrades)
    dfGrades.columns = ["id", "grade", "locale"]
    return dfGrades


def getPricingFromDB():
    pricingDevicesSelect = select([
        pricingDevices.columns.device_price_id,
        pricingDevices.columns.device_id

    ])
    resultPricingDevices = connection.execute(pricingDevicesSelect).fetchall()
    dfPricingDevices = pd.DataFrame(resultPricingDevices)
    dfPricingDevices.columns = ["device_price_id", "device_id"]
    return dfPricingDevices


def getPricingNetworkFromDB():
    pricingDeviceNetworkSelect = select([
        pricingDeviceNetwork.columns.device_price_id,
        pricingDeviceNetwork.columns.network_id

    ])
    resultpricingDeviceNetwork = connection.execute(
        pricingDeviceNetworkSelect).fetchall()
    dfNetworks = pd.DataFrame([f._mapping for f in resultpricingDeviceNetwork])
    dfNetworks = pd.DataFrame(resultpricingDeviceNetwork)
    dfNetworks.columns = ["device_price_id", "network_id"]
    return dfNetworks


def getPricingCSV():

    # scopes = ["https://www.googleapis.com/auth/drive",
    #           "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
    # secret_file = os.path.join(os.getcwd(), 'gbt-data/gbt-creds.json')
    # spreadsheet_id = '1Py1GJ8ACb3cwZ_-GDAg79ipOaeLdv7CsBQK2RyDbFIs'
    # range_name = 'Sheet1!A1:K1'
    # credentials = service_account.Credentials.from_service_account_file(
    #     secret_file, scopes=scopes)
    # service = discovery.build('sheets', 'v4', credentials=credentials)
    # data = {
    #     "values": ["aaa", "bb"]
    # }
    # service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, body=data,
    #                                        range=range_name, valueInputOption='USER_ENTERED').execute()

    # print(service)
    pricing = pd.read_csv(f'gbt-data/pricing_update_template.csv')
    return pricing


pricingDeviceCapacity


def getPricingDeviceCapacity():
    pricingDeviceCapacitySelect = select([
        pricingDeviceCapacity.columns.device_price_id,
        pricingDeviceCapacity.columns.capacity_id

    ])
    resultPricingDeviceCapacity = connection.execute(
        pricingDeviceCapacitySelect).fetchall()
    dfPricingDeviceCapacity = pd.DataFrame(resultPricingDeviceCapacity)
    dfPricingDeviceCapacity.columns = ["device_price_id", "capacity_id"]
    return dfPricingDeviceCapacity


def getPricingDeviceGrades():
    pricingDeviceGradeSelect = select([
        pricingDeviceGrades.columns.device_price_id,
        pricingDeviceGrades.columns.grade_id

    ])
    resultPricingDeviceGrade = connection.execute(
        pricingDeviceGradeSelect).fetchall()
    dfPricingDeviceGrade = pd.DataFrame(resultPricingDeviceGrade)
    dfPricingDeviceGrade.columns = ["device_price_id", "grade_id"]
    return dfPricingDeviceGrade


def getManufacturers():
    manufacturesSelect = select([
        manufacturers.columns.id,
        manufacturers.columns.name

    ])
    resultManufacturers = connection.execute(manufacturesSelect).fetchall()
    dfManufacturers = pd.DataFrame(resultManufacturers)
    dfManufacturers.columns = ["id", "name"]
    return dfManufacturers
