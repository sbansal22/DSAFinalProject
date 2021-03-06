import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def check_dead_ends(df):
    df.drop(df.loc[df['to']=='Dead End'].index, inplace=True)


def querry_geopy(st1, st2, idx, df, attempt=1, max_attempts=5):
    try: 
        # set up the geolocator and find lat/long
        geolocator = Nominatim(user_agent="google maps")
        st1_com = st1 + ', Bostn, Massachusetts'
        st2_com = st2 + ', Boston, Massachusetts'
        st1_loc = geolocator.geocode(st1_com)
        st2_loc = geolocator.geocode(st2_com)

        # case when querrying the lat/long of st1 or st2 fails
        if st1_loc is None or st2_loc is None:
            # put a placeholder value that indicates Error
            df.loc[idx, 'st1_lat'] = 'Querry Failed'
            df.loc[idx, 'st1_long'] = 'Querry Failed'
            df.loc[idx, 'st2_lat'] = 'Querry Failed'
            df.loc[idx, 'st2_long'] = 'Querry Failed'

        # case when querrying the lat/long of st1 or st2 succeeds
        else:
            # write the lat/long in the dataframe
            df.loc[idx, 'st1_lat'] = st1_loc.latitude
            df.loc[idx, 'st1_long'] = st1_loc.longitude
            df.loc[idx, 'st2_lat'] = st2_loc.latitude
            df.loc[idx, 'st2_long'] = st2_loc.longitutde

    except GeocoderTimedOut:
        if attempt <= max_attempts:
            return querry_geopy(st1, st2, idx, df, attempt=attempt+1)
        raise
    

def process_df():
    ### initialization ###
    data = pd.read_excel(r'St-Data-Original.xlsx')

    df = pd.DataFrame(data)
    st_name = df['St_name']
    from_st = df['from']
    to_st = df['to']
    miles = df['miles']
    # make lat and log as columns with default numbers here
    df['st1_lat'] = 0.0 ; st1_lat = df['st1_lat']
    df['st1_long'] = 0.0 ; st1_long = df['st1_long']
    df['st2_lat'] = 0.0 ; st2_lat = df['st2_lat']
    df['st2_long'] = 0.0 ; st2_long = df['st2_long']

    # find all dead_ends and delete rows that contain dead ends
    check_dead_ends(df)

    # find all streets that geopy cannot find the lat/long
    for idx in range(len(df.index)):
        querry_geopy(from_st[idx], to_st[idx], idx, df)

    # delete all rows that geopy failed to pinpoint the lat/long
    df.drop(df.loc[df['st1_lat']=='Querry Failed'].index, inplace=True)
    df.drop(df.loc[df['st1_long']=='Querry Failed'].index, inplace=True)
    df.drop(df.loc[df['st2_lat']=='Querry Failed'].index, inplace=True)
    df.drop(df.loc[df['st2_long']=='Querry Failed'].index, inplace=True)

    print(df)
    return df


if __name__ == "__main__":
    df_processed = process_df()
    print(df_processed)

