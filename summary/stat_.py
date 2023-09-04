from pandas import DataFrame, to_datetime
from datetime import timedelta
import math


def analyze_risk(df):
    df['event'] = df['status']
    df['risk_percentage'] = 0

    df.loc[df['event'] == 'report', 'risk_percentage'] = 0
    df.loc[df['event'] == 'fail', 'risk_percentage'] = 0
    df.loc[df['event'] == 'launch_campaign', 'risk_percentage'] = 0
    df.loc[df['event'] == 'send_email', 'risk_percentage'] = 0
    df.loc[df['event'] == 'open_email', 'risk_percentage'] = 25
    df.loc[df['event'] == 'click_link', 'risk_percentage'] = 75
    df.loc[df['event'] == 'submit_data', 'risk_percentage'] = 100


def analyze_campaign(df: DataFrame) -> tuple[DataFrame, dict]:
    '''Calculate Mean and Std of Result'''

    analyze_risk(df)
    df["submit_date"] = to_datetime(df["submit_date"])
    df["send_date"] = to_datetime(df["send_date"])
    df["open_date"] = to_datetime(df["open_date"])
    df["click_date"] = to_datetime(df["click_date"])
    df["report_date"] = to_datetime(df["report_date"])
    # Calculate time difference between send_date and submit_date for submitted_data
    df["time_sent_to_submit"] = df["submit_date"] - df["send_date"]
    df["time_sent_to_open"] = df["open_date"] - df["send_date"]
    df["time_open_to_click"] = df["click_date"] - df["open_date"]
    df["time_click_to_submit"] = df["submit_date"] - df["click_date"]
    df["time_sent_to_report"] = df["report_date"] - df["send_date"]

    # Calculate the mean of 'risk_percentage' column
    mean_risk_percentage = df['risk_percentage'].mean()
    mean_time_sent_to_submit = df['time_sent_to_submit'].mean()
    mean_time_sent_to_open = df['time_sent_to_open'].mean()
    mean_time_open_to_click = df['time_open_to_click'].mean()
    mean_time_click_to_submit = df['time_click_to_submit'].mean()
    mean_time_sent_to_report = df['time_sent_to_report'].mean()

    std_risk_percentage = df['risk_percentage'].std()
    std_time_sent_to_submit = df['time_sent_to_submit'].std()
    std_time_sent_to_open = df['time_sent_to_open'].std()
    std_time_open_to_click = df['time_open_to_click'].std()
    std_time_click_to_submit = df['time_click_to_submit'].std()
    std_time_sent_to_report = df['time_sent_to_report'].std()

    analyzed = dict()
    analyzed["mean_risk_percentage"] = mean_risk_percentage
    analyzed["mean_time_sent_to_submit"] = mean_time_sent_to_submit
    analyzed["mean_time_sent_to_open"] = mean_time_sent_to_open
    analyzed["mean_time_open_to_click"] = mean_time_open_to_click
    analyzed["mean_time_click_to_submit"] = mean_time_click_to_submit
    analyzed["mean_time_sent_to_report"] = mean_time_sent_to_report

    analyzed["std_risk_percentage"] = std_risk_percentage
    analyzed["std_time_sent_to_submit"] = std_time_sent_to_submit
    analyzed["std_time_sent_to_open"] = std_time_sent_to_open
    analyzed["std_time_open_to_click"] = std_time_open_to_click
    analyzed["std_time_click_to_submit"] = std_time_click_to_submit
    analyzed["std_time_sent_to_report"] = std_time_sent_to_report

    return df, analyzed


def get_res(a: list):

    df = DataFrame.from_records(a)
    analysis_result, analysis_dict = analyze_campaign(df)
    # Convert DataFrame to a dictionary

    result_dict = analysis_result.to_dict(orient='records')
    # # Convert time-related columns to the correct format
    # result_dict = format_time_columns(result_dict)

    return result_dict, analysis_dict


############# For export Excel #################


def analyze_campaign_export(df: DataFrame) -> tuple[DataFrame, dict]:
    '''Calculate Mean and Std of Result'''
    # print("-------------------Analyzation-------------------------")
    analyze_risk(df)
    # print(df.head())
    df["submit_date"] = to_datetime(df["submit_date"])
    df["send_date"] = to_datetime(df["send_date"])
    df["open_date"] = to_datetime(df["open_date"])
    df["click_date"] = to_datetime(df["click_date"])
    df["report_date"] = to_datetime(df["report_date"])
    # Calculate time difference between send_date and submit_date for submitted_data
    df["time_sent_to_submit"] = df["submit_date"] - df["send_date"]
    df["time_sent_to_open"] = df["open_date"] - df["send_date"]
    df["time_open_to_click"] = df["click_date"] - df["open_date"]
    df["time_click_to_submit"] = df["submit_date"] - df["click_date"]
    df["time_sent_to_report"] = df["report_date"] - df["send_date"]

    # change to seconds for import data to update
    df["time_sent_to_submit"] = df["time_sent_to_submit"].apply(
        lambda x: x.total_seconds())
    df["time_sent_to_open"] = df["time_sent_to_open"].apply(
        lambda x: x.total_seconds())
    df["time_open_to_click"] = df["time_open_to_click"].apply(
        lambda x: x.total_seconds())
    df["time_click_to_submit"] = df["time_click_to_submit"].apply(
        lambda x: x.total_seconds())
    df["time_sent_to_report"] = df["time_sent_to_report"].apply(
        lambda x: x.total_seconds())

    mean_risk_percentage = df['risk_percentage'].mean()
    mean_time_sent_to_submit = df['time_sent_to_submit'].mean()
    mean_time_sent_to_open = df['time_sent_to_open'].mean()
    mean_time_open_to_click = df['time_open_to_click'].mean()
    mean_time_click_to_submit = df['time_click_to_submit'].mean()
    mean_time_sent_to_report = df['time_sent_to_report'].mean()

    std_risk_percentage = df['risk_percentage'].std()
    std_time_sent_to_submit = df['time_sent_to_submit'].std()
    std_time_sent_to_open = df['time_sent_to_open'].std()
    std_time_open_to_click = df['time_open_to_click'].std()
    std_time_click_to_submit = df['time_click_to_submit'].std()
    std_time_sent_to_report = df['time_sent_to_report'].std()

    analyzed = dict()
    analyzed["mean_risk_percentage"] = mean_risk_percentage
    analyzed["mean_time_sent_to_submit"] = mean_time_sent_to_submit
    analyzed["mean_time_sent_to_open"] = mean_time_sent_to_open
    analyzed["mean_time_open_to_click"] = mean_time_open_to_click
    analyzed["mean_time_click_to_submit"] = mean_time_click_to_submit
    analyzed["mean_time_sent_to_report"] = mean_time_sent_to_report

    analyzed["std_risk_percentage"] = std_risk_percentage
    analyzed["std_time_sent_to_submit"] = std_time_sent_to_submit
    analyzed["std_time_sent_to_open"] = std_time_sent_to_open
    analyzed["std_time_open_to_click"] = std_time_open_to_click
    analyzed["std_time_click_to_submit"] = std_time_click_to_submit
    analyzed["std_time_sent_to_report"] = std_time_sent_to_report
    return df, analyzed

# change format time { 0 Day 00:00:00} when recive data unit seconds


def format_time(seconds):
    if seconds == 'FALSE':
        return seconds

    if math.isnan(seconds):  # เพิ่มการตรวจสอบสำหรับค่า NaN
        return 'FALSE'
    days = seconds // (24 * 3600)
    seconds %= (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    formatted_time = f"{int(days)} Day {int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    return formatted_time

# use defult from get_res


def get_res_ex(a: list):

    df = DataFrame.from_records(a)
    # change to analyze_campaign --> analyze_campaign_export
    analysis_result, analysis_dict = analyze_campaign_export(df)

    result_dict = analysis_result.to_dict(orient='records')

    return result_dict, analysis_dict
