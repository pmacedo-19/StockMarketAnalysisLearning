from app.services import fetch_stock_data

def test_fetch_stock_data(mocker):
    mock_response = {"c": 100.0, "h": 110.0, "l": 90.0, "o": 95.0, "pc": 98.0}
    mocker.patch("requests.get", return_value=mocker.Mock(json=lambda: mock_response))
    data = fetch_stock_data("AAPL")
    assert data["c"] == 100.0
