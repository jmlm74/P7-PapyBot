import requests
import json
import pytest


import papybot.utils.query as query
import papybot.utils.api as api
from papybot import app
import os


# pytest fixture to init test functions
@pytest.fixture
def client():
    app.config['TESTING'] = True


# test homepage return 200
def test_index_page_return200():
    with app.test_client() as clt:
        rc = clt.get('/index/')
        assert rc.status_code == 200


# test 404 page return 404 and not 200
def test_foobar_return404():
    with app.test_client() as clt:
        rc = clt.get('/foobar/')
        assert rc.status_code == 404


# test parser stand alone
def test_parser_ok():
    """
        Test the parser in stand alone
    """
    req = query.Query("Salut GrandPy ! sais tu quelle est la capitale de la Bulgarie ? Merci !")
    result = req.parse_query()
    assert result == "capitale bulgarie"


# test gooapi
def test_gooapi_ok(monkeypatch):
    """
        Test the google API on file
        Must return a good latitude
    """
    class MockResp:
        """
        Mock the requests.get
        status_code is the http code response
        json() is to mock requests.json() and simulate the json response of requests.get by reading the
        file which is in fact the json return of the API request  -->
            The return is the same as requests.get --> get in a sample file in static/api
        """
        def __init__(self):
            self.status_code = 200

        def json(self):
            fic_json = str(app.root_path) + '/static/api/1.json'
            json_data = open(fic_json, 'r')
            text = json_data.read()
            json_data.close()
            json_response = {}
            json_response = json.loads(text)
            return json_response

    # the file 1.json contains the real return of google api for the address of the eiffel tower
    testgooapi = api.Gooapi('adresse tour eiffel')

    def mock_request_get(url):
        mock_resp = MockResp()
        return mock_resp

    monkeypatch.setattr('requests.get', mock_request_get)
    tab_result = testgooapi.get_json()
    assert tab_result['latitude'] == 48.85837009999999


def test_gooapi_resultnotok(monkeypatch):
    """
        Test the Google API --> bad request or Zero Result --> Nothing returned
        --> must return Error
    """
    class MockResp:
        """
        Mock the requests.get
        status_code is the http code response
        json() is to mock requests.json() and simulate the json response of requests.get by reading the
        file which is in fact the json return of the API request  -->
            The return is the same as requests.get --> get in a sample file in static/api
        The test is to get a return-address as 'Error' --> the status is not OK 
            (ZERO RESULT or BAD REQUEST)
        """
        def __init__(self):
            self.status_code = 200

        def json(self):
            fic_json = str(app.root_path) + '/static/api/2.json'
            json_data = open(fic_json, 'r')
            text = json_data.read()
            json_data.close()
            json_response = {}
            json_response = json.loads(text)
            return json_response

    # the file 1.json contains the real return of google api for the address of the eiffel tower
    testgooapi = api.Gooapi('toto titi tata')

    def mock_request_get(url):
        mock_resp = MockResp()
        return mock_resp

    monkeypatch.setattr('requests.get', mock_request_get)
    tab_result = testgooapi.get_json()
    assert tab_result['address'] == 'Error'


# test wikiapi
def test_wikiapi_ok(monkeypatch):
    """
        test the wiki api on files
        --> openclassrooms wiki page
        --> must return the name  openclassroom
    """
    class MockResp:
        """
        Mock the requests.get
        status_code is the http code response
        json() is to mock requests.json() and simulate the json response of requests.get by reading the
        file which is in fact the json return of the API request  -->
            The return is the same as requests.get --> get in a sample file in static/api
        The class variable "passed" is used because we use requests.json() 2 times in the same method and
        each time we reinstance the class MockResp So I needed a class variable to have a counter too open
            2 differents files
        """
        passed = 0

        def __init__(self):
            self.status_code = 200

        def json(self):
            if MockResp.passed == 0:
                fic_json = str(app.root_path) + '/static/api/10.json'
                MockResp.passed += 1
            else:
                fic_json = str(app.root_path) + '/static/api/11.json'
            json_data = open(fic_json, 'r')
            text = json_data.read()
            json_data.close()
            json_response = {}
            json_response = json.loads(text)
            return json_response

    test_wikiapi = api.Wikiapi("Tour Eiffel")

    def mock_request_get(url):
        mock_resp = MockResp()
        return mock_resp

    monkeypatch.setattr('requests.get', mock_request_get)
    result = test_wikiapi.get_json()
    assert result['extract'][0:14] == 'OpenClassrooms'


def test_wikiapi_erreur(monkeypatch):
    """
        Test the wiki API  on a blank page --> nothing returned by wiki
        --> must return error
    """
    class MockResp:
        """
        Mock the requests.get
        status_code is the http code response
        json() is to mock requests.json() and simulate the json response of requests.get by reading the
        file which is in fact the json return of the API request  -->
            The return is the same as requests.get --> get in a sample file in static/api
        The class variable "passed" is used because we use requests.json() 2 times in the same method and
        each time we reinstance the class MockResp So I needed a class variable to have a counter too open
            2 differents files
        """
        passed = 0

        def __init__(self):
            self.status_code = 200

        def json(self):
            if MockResp.passed == 0:
                fic_json = str(app.root_path) + '/static/api/12.json'
                MockResp.passed += 1
            else:
                fic_json = str(app.root_path) + '/static/api/12.json'
            json_data = open(fic_json, 'r')
            text = json_data.read()
            json_data.close()
            json_response = {}
            json_response = json.loads(text)
            return json_response

    test_wikiapi = api.Wikiapi("FooBar nada nothing to return")

    def mock_request_get(url):
        mock_resp = MockResp()
        return mock_resp

    monkeypatch.setattr('requests.get', mock_request_get)
    result = test_wikiapi.get_json()
    assert result['error'] is True
