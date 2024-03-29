import pytest
from mock import MagicMock
from app.http_client.APIAdresse import APIAdresse

@pytest.fixture()
def address_api():
    return APIAdresse()


api_adresse_response = {"type": "FeatureCollection", "version": "draft", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [2.378185, 48.898595]},
         "properties": {"label": "157 Boulevard Macdonald 75019 Paris", "score": 0.8252954545454545,
                        "housenumber": "157", "id": "75119_5876_00157", "name": "157 Boulevard Macdonald",
                        "postcode": "75019", "citycode": "75119", "x": 654412.35, "y": 6866689.51, "city": "Paris",
                        "district": "Paris 19e Arrondissement", "context": "75, Paris, Île-de-France",
                        "type": "housenumber", "importance": 0.82825, "street": "Boulevard Macdonald"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [2.394186, 48.886931]},
         "properties": {"label": "157 Boulevard Sérurier 75019 Paris", "score": 0.5197946280991735,
                        "housenumber": "157", "id": "75119_8939_00157", "name": "157 Boulevard Sérurier",
                        "postcode": "75019", "citycode": "75119", "x": 655575.47, "y": 6865383.41, "city": "Paris",
                        "district": "Paris 19e Arrondissement", "context": "75, Paris, Île-de-France",
                        "type": "housenumber", "importance": 0.80865, "street": "Boulevard Sérurier"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [2.396588, 48.885313]},
         "properties": {"label": "Boulevard d'Indochine 75019 Paris", "score": 0.4941895867768594, "id": "75119_4702",
                        "name": "Boulevard d'Indochine", "postcode": "75019", "citycode": "75119", "x": 655750.23,
                        "y": 6865202.15, "city": "Paris", "district": "Paris 19e Arrondissement",
                        "context": "75, Paris, Île-de-France", "type": "street", "importance": 0.73154,
                        "street": "Boulevard d'Indochine"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [2.370575, 48.878577]},
         "properties": {"label": "Boulevard de la Villette 75019 Paris", "score": 0.42279389610389606,
                        "id": "75119_9838", "name": "Boulevard de la Villette", "postcode": "75019",
                        "citycode": "75119", "x": 653836.7, "y": 6864468.03, "city": "Paris",
                        "district": "Paris 19e Arrondissement", "context": "75, Paris, Île-de-France", "type": "street",
                        "importance": 0.79359, "street": "Boulevard de la Villette"}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [2.368835, 48.886621]},
         "properties": {"label": "Rue du Maroc 75019 Paris", "score": 0.3785455844155844, "id": "75119_6114",
                        "name": "Rue du Maroc", "postcode": "75019", "citycode": "75119", "x": 653716.24,
                        "y": 6865363.5, "city": "Paris", "district": "Paris 19e Arrondissement",
                        "context": "75, Paris, Île-de-France", "type": "street", "importance": 0.73543,
                        "street": "Rue du Maroc"}}], "attribution": "BAN", "licence": "ETALAB-2.0",
     "query": "157 boulevard Mac Donald 75019 Paris", "limit": 5
}

expected_result = {'x': 2.378185, 'y': 48.898595}

@pytest.mark.parametrize(
    "query, mock_response, expected",
    [
        pytest.param({}, {}, {}),
        pytest.param(
            {
                "id1": "157 boulevard Mac Donald 75019 Paris",
            },
            api_adresse_response,
            expected_result
        )
    ]
)
def test_get_address_coordinates(monkeypatch, address_api, query, mock_response, expected):
    monkeypatch.setattr(APIAdresse, "send_request", MagicMock(return_value=mock_response))
    result = address_api.get_address_coordinates(query)
    assert result == expected
