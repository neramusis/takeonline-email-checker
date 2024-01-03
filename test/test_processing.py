import json

import pytest

from run import process_email


@pytest.mark.asyncio
async def test_email_1():
    file_path = 'test/fixtures/1101917483_JL_2023-12-11T20:05:46Z.json'
    with open(file_path, 'r') as file:
        email_content = json.load(file)

    result = await process_email(order_id="1101917483", email=email_content)

    expected_result = {
        'status': 2,
        'tracking_id': 'CB070035134FR',
    }
    assert result == expected_result, f"Expected {expected_result}, got {result}"


@pytest.mark.asyncio
async def test_email_2():
    file_path = 'test/fixtures/21071223180631102_DS_2023-12-08T12:24:00Z.json'
    with open(file_path, 'r') as file:
        email_content = json.load(file)

    result = await process_email(order_id="21071223180631102", email=email_content)

    expected_result = {
        'status': 2,
        'tracking_id': '1000689586728U',
    }
    assert result == expected_result, f"Expected {expected_result}, got {result}"


@pytest.mark.asyncio
async def test_email_3():
    file_path = 'test/fixtures/434475740_DS_2023-12-05T13:16:43Z.json'
    with open(file_path, 'r') as file:
        email_content = json.load(file)

    result = await process_email(order_id="434475740", email=email_content)

    expected_result = {
        'status': 2,
        'tracking_id': '9V31898536593',
    }
    assert result == expected_result, f"Expected {expected_result}, got {result}"


@pytest.mark.asyncio
async def test_email_4():
    file_path = 'test/fixtures/7246174_DS_2023-12-07T09:06:39Z.json'
    with open(file_path, 'r') as file:
        email_content = json.load(file)

    result = await process_email(order_id="7246174", email=email_content)

    expected_result = {
        'status': 2,
        'tracking_id': '1000687998601U',
    }
    assert result == expected_result, f"Expected {expected_result}, got {result}"


@pytest.mark.asyncio
async def test_email_5():
    file_path = 'test/fixtures/27201249613_ad_2023-12-22T08:45:56Z.json'
    with open(file_path, 'r') as file:
        email_content = json.load(file)

    result = await process_email(order_id="27201249613", email=email_content)

    expected_result = {'status': 2, 'tracking_id': '287798I077590'}
    assert result == expected_result, f"Expected {expected_result}, got {result}"
