from math import sin, cos, sqrt, atan2,radians
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from geopy.geocoders import Nominatim

def location_finder(address):
  
  #address we need to geocode
  loc = address
  try:
    #making an instance of Nominatim class
    geolocator = Nominatim(user_agent="my_request")
    
    #applying geocode method to get the location
    location = geolocator.geocode(loc)
    latitude = location.latitude
    longitude = location.longitude
    return latitude, longitude
  except:
    print("Error in address")
    return None, None
def spoton(lat, lng, rad, dictionary, data):
  #Declarations:
  albilad_avg_traffic = 45.73
  other_banks_avg_traffic = 39.30
  perc_avg_diff = round(((albilad_avg_traffic-other_banks_avg_traffic)/other_banks_avg_traffic)*100, 2)
  
  newlat=lat
  newlon=lng
  radius = rad 
  def getDist(lat1,lon1,lat2,lon2):
    R = 6373.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

  data['distance']=list(map(lambda k: getDist(data.loc[k]['Lat'],data.loc[k]['Lng'],newlat,newlon), data.index))
  #Get subset data
  subset_data = data[data['distance']<radius]
  #Returning NULL if no banks in that area
  if(len(subset_data) == 0):
    return None, None, None, None
  else:
    #Normalize
    # from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    normalized_subset_data=subset_data
    normalized_subset_data[['Avg_Traffic_normalized', 'Time1', 'Time2', 'Time3', 'Time4', 'Time5', 'Time6', 'Time7', 'Time8', 'Time9', 'Time10', 
                    'Time11', 'Time12', 'Time13', 'Time14', 'Time15', 'Time16', 'Time17', 'Time18', 'Time19', 'Time20',
                    'Time21', 'Time22', 'Time23', 'Time24']] = scaler.fit_transform(subset_data[['Avg_Traffic', 'Time1', 'Time2', 'Time3', 'Time4', 'Time5', 'Time6', 'Time7', 'Time8', 'Time9', 'Time10', 
                    'Time11', 'Time12', 'Time13', 'Time14', 'Time15', 'Time16', 'Time17', 'Time18', 'Time19', 'Time20',
                    'Time21', 'Time22', 'Time23', 'Time24']])
    avg_traffic_min = normalized_subset_data['Avg_Traffic'].min() 
    avg_traffic_max = normalized_subset_data['Avg_Traffic'].max()
    dictionary = dictionary.iloc[: , 1:]
    test = normalized_subset_data.merge(dictionary, on="Place_id", how="left")
    test = test.drop(['Lat_y', 'Lng_y', 'Rating','Rating_n'], 1)
    albilad = test[~test['Albilad'].isnull()]
    other_banks = test[test['Albilad'].isnull()]
    #############################################
    #Final Output
    if len(albilad)<=0:
      value_albilad = round(other_banks['Avg_Traffic'].mean()*(1+(perc_avg_diff/100)),2)
      #print("AVERAGE OF AL BILAD BANK IS:", value_albilad)
      normalized_value_albilad = round((value_albilad - avg_traffic_min) / (avg_traffic_max - avg_traffic_min),2)
      #print("The normalized value of that foot traffic would be", normalized_value_albilad)
      value_other_banks = round(other_banks['Avg_Traffic'].mean(),2)
      #print("AVERAGE OF OTHER BANKS IS:", value_other_banks)
      albilad_perc_avg_diff = round(((value_albilad-value_other_banks)/value_other_banks)*100, 2)
      #print("Percent average difference is:", albilad_perc_avg_diff)
      return value_albilad, value_other_banks, albilad_perc_avg_diff, False
    else:
      value_albilad = round(albilad['Avg_Traffic'].mean(),2)
      normalized_value_albilad = round((value_albilad - avg_traffic_min) / (avg_traffic_max - avg_traffic_min),2)
      #print("AVERAGE OF AL BILAD BANK IS:", value_albilad)
      #print("Normalized value OF AL BILAD BANK IS:", normalized_value_albilad)
      value_other_banks = round(other_banks['Avg_Traffic'].mean(),2)
      normalized_value_other_banks = round((value_other_banks - avg_traffic_min) / (avg_traffic_max-avg_traffic_min),2)
      #print("AVERAGE OF OTHER BANKS IS:", value_other_banks)
      #print("Normalized value OF Other BANK IS:", normalized_value_other_banks)
      albilad_perc_avg_diff = round(((value_albilad-value_other_banks)/value_other_banks)*100, 2)
      #print("Percent average difference is:", albilad_perc_avg_diff)
      return value_albilad, value_other_banks, albilad_perc_avg_diff, True