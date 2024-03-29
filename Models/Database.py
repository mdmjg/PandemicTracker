import pymysql.cursors
from Models.CountryList import CountryList
from Models.StatsScraper import StatsScraper
from Models.TravelScraper import TravelScraper
from Models.HealthcareScraper import HealthcareScraper
from datetime import date


class Database:
    def __init__(self):
        # Configure MySQL
        self.conn = pymysql.connect(
            host="localhost",
            port=8889,
            user="root",
            password="root",
            db="PandemicTracker",
            charset="utf8",
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.CountryList = CountryList()
        self.StatsScraper = StatsScraper()
        self.TravelScraper = TravelScraper()
        self.Healthcare = HealthcareScraper()
        self.totalDeaths = 0
        self.totalRecovered = 0
        self.totalCases = 0
        self.date = 0

    def searchCountry(self, country):
        print(country)
        cursor = self.conn.cursor()
        query = "SELECT * FROM Country WHERE countryName = %s"
        cursor.execute(query, country)
        data = cursor.fetchall()
        cursor.close()
        return data

    ## displays all countries
    def viewCountry(self):
        cursor = self.conn.cursor()
        query = "SELECT countryName, numCases, numDeaths, numRecovered, numDoctors, numHospitalBeds, latestTravelRestriction FROM Country"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data

    def addCountries(self):
        cursor = self.conn.cursor()
        query = "INSERT INTO Country (countryName, numCases, numDeaths, numRecovered, numDoctors, numHospitalBeds, latestTravelRestriction) VALUES (%s, 0, 0, 0, 0, 0, NULL)"
        for country in self.CountryList.countryList:
            cursor.execute(query, country)
            self.conn.commit()
        cursor.close()
        print("success")

    def updateCountryHealthcare(self, country, numDoctors, numHospitalBeds):
        cursor = self.conn.cursor()
        query = "UPDATE Country SET numDoctors = %s, numHospitalBeds = %s WHERE countryName = %s"
        cursor.execute(query, (numDoctors, numHospitalBeds, country))
        self.conn.commit()
        cursor.close()

    def updateCountryStats(self, country, numCases, numDeaths, numRecovered):
        cursor = self.conn.cursor()
        query = "UPDATE Country SET numCases = %s, numDeaths = %s, numRecovered = %s WHERE countryName = %s"
        cursor.execute(query, (numCases, numDeaths, numRecovered, country))
        self.conn.commit()
        cursor.close()

    def updateCountryTravelRestrictions(self, country, latestTravelRestriction):
        cursor = self.conn.cursor()
        query = "UPDATE Country SET latestTravelRestriction = %s WHERE countryName = %s"

        cursor.execute(query, (latestTravelRestriction, country))
        self.conn.commit()
        cursor.close()

    def updateWorldStats(self):
        self.totalCases = StatsScraper.globalConfirmed
        self.totalDeaths = StatsScraper.globalDeaths
        self.totalRecovered = StatsScraper.globalRecovered

    def updateAllCountriesHospitalBeds(self):
        health = self.Healthcare.scrapeHealthcare()
        if health.empty:
            print("health is none")
        else:
            for index, row in health.iterrows():
                countryName = row["countryName"]
                numDoctors = row["numDoctors"]
                numHospitalBeds = row["numHospitalBeds"]
                self.updateCountryHealthcare(countryName, numDoctors, numHospitalBeds)
        print("hospital beds updated")

    def updateAllCoutriesStats(self):
        allCases = self.StatsScraper.scrapeCases()
        df = allCases[0]

        if df.empty:
            print("none")
        else:
            for index, row in df.iterrows():
                countryName = row["countryName"]
                numCases = row["numCases"]
                numDeaths = row["numDeaths"]
                numRecovered = row["numRecovered"]
                self.updateCountryStats(
                    countryName, int(numCases), int(numDeaths), (numRecovered)
                )
            print("stats updated")

    def updateAllCountriesTravel(self):
        travel = self.TravelScraper.scrapeTravel()
        if travel.empty:
            print("None")
        else:
            for index, row in travel.iterrows():
                countryName = row["countryName"]
                latestTravelRestriction = row["travelAdv"]
                self.updateCountryTravelRestrictions(
                    countryName, latestTravelRestriction
                )
            print("travel updated")

    def updateAll(self):
        if date.today() == self.date:
            return
        else:
            self.updateAllCountriesHospitalBeds()
            self.updateAllCoutriesStats()
            # self.updateAllCountriesTravel()
            self.updateWorldStats()
            print("everything was updated")
            self.date = date.today()
