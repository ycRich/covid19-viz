import pandas as pd
from us_state_abbrev import us_state_abbrev

def get_us_state(df):
    df = df[(df['Country/Region']=='US')]
    df['Province/State'] = df['Province/State'].apply(lambda x: us_state_abbrev.get(x, None))
    df = df[df['Province/State'].notnull()]
    return df.reset_index()


def get_us_county(df):
    df = df[df['FIPS'].notnull()]
    df['FIPS'] = df['FIPS'].str.zfill(5)
    return df


def load_state_timeseries():
    TIMESERIES_URLS = {
        "confirmed": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv",
        "deaths": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv",
        "recovered": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"
    }
    
    res = {}
    for x in TIMESERIES_URLS:
        tmp = get_us_state(pd.read_csv(TIMESERIES_URLS[x])).set_index('Province/State')
        tmp_t = tmp.iloc[:,4:].transpose().reset_index()
        tmp_tidy = pd.melt(tmp_t, id_vars=['index'], value_vars=[x for x in tmp_t.columns if x!='index'])
        tmp_tidy.rename(columns={'index':'date', 'value':'Number of Cases'}, inplace=True)
        res[x] = tmp_tidy[(pd.to_datetime(tmp_tidy['date']) >= pd.to_datetime('03-10-2020')) & (pd.to_datetime(tmp_tidy['date']) <= pd.to_datetime('03-22-2020'))]
    return res


def load_key_country_timeseries():
    URL = "https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv"
    key_countries = ['China', 'US', 'United Kingdom', 'Italy', 'France', 'Germany', 'Spain', 'Iran']
    df = pd.read_csv(URL, parse_dates=['Date'])
    df = df[df['Country'].isin(key_countries)]
    return df


def load_state_daily_report(date):
    DAILY_REPORT_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv".format(date)
    try:
        if pd.to_datetime(date) <= pd.to_datetime('03-21-2020'):
            report = pd.read_csv(DAILY_REPORT_URL)
            report = get_us_state(report)
        else:
            report = pd.read_csv(DAILY_REPORT_URL, dtype={'FIPS':str})
            report = get_us_county(report)
        report['Active'] = report['Confirmed'] - report['Deaths'] - report['Recovered']
        return report
    except Exception as e:
        print(e)
        print("please provide a valid date in MM-DD-YY format")