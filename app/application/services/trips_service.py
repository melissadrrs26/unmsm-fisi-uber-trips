
import json
from polars import DataFrame, col, concat_list, lit, Utf8
from ...infrastructure import TripsRepository
from ...utils import enum

class TripsService:

    async def set_trips_json(self, date_code:str):

        cols = ["timestamp","centroid_lat","centroid_lon","type_code","value"]
        df_anomalous = await TripsRepository().get_trips(enum.TYPE_TRIP.Anomalous.value, date_code)
        df_anomalous = df_anomalous.with_columns( type_code = lit(enum.TYPE_TRIP.Anomalous.value, Utf8))
        df_anomalous = df_anomalous.select(cols)
        df_anomalous = df_anomalous.rename({
            "timestamp":"time_index",
            "centroid_lat": "latitud",
            "centroid_lon": "longitud",
            "value":"data"
        })

        df_non_anomalous = await TripsRepository().get_trips(enum.TYPE_TRIP.NoAnomalous.value, date_code)
        df_non_anomalous = df_non_anomalous.with_columns( type_code = lit(enum.TYPE_TRIP.NoAnomalous.value, Utf8))
        df_non_anomalous = df_non_anomalous.select(cols)
        df_non_anomalous = df_non_anomalous.rename({
            "timestamp":"time_index",
            "centroid_lat": "latitud",
            "centroid_lon": "longitud",
            "value":"data"
        })

       
        df_data:DataFrame = df_anomalous.extend(df_non_anomalous)
        df_data = df_data.with_columns( data = concat_list(["latitud","longitud"]))
        df_data = df_data.group_by("type_code","time_index").agg("data")

        dict_anomalous =  df_data.filter(col("type_code") == enum.TYPE_TRIP.Anomalous.value).select("time_index","data").to_dict()
        dict_non_anomalous = df_data.filter(col("type_code") == enum.TYPE_TRIP.NoAnomalous.value).select("time_index","data").to_dict()

        dict_anomalous = {k: v.to_list() for k, v in dict_anomalous.items()}
        dict_non_anomalous = {k: v.to_list() for k, v in dict_non_anomalous.items()}

        data_js = {}
        data_js[enum.TYPE_TRIP.Anomalous.value] =  dict_anomalous
        data_js[enum.TYPE_TRIP.NoAnomalous.value] = dict_non_anomalous

        return data_js