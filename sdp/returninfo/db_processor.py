
class DbProcessor:
    def __init__(self, conn):
        self.conn = conn

    def update_sdp_classifications(self, deployment_frequency, lead_time, release_id):
        cursor_delete = self.conn.cursor()
        sql_delete = "DELETE FROM SDPClassificationsReleases WHERE IdRelease = ?;"
        cursor_delete.execute(sql_delete, [release_id])
        self.conn.commit()

        sdp_classifications_id = 0
        '''
            High Performers (sdp_classifications_id = 1)
                * deployment_frequency: multiple deploys per day {< 24 [hours]}
                * lead_time: less than 1 hour {< 1 [hour]}
            Medium Performers (sdp_classifications_id = 2)
                * deployment_frequency: between once per week and one month { > 24 AND <= 730 [hours]}
                * lead_time: between one week and one month {> 1 AND <= 730 [hours]}
            Low Performers (sdp_classifications_id = 3)
                * deployment_frequency: more than one month {> 730 [hours]}
                * lead_time: more than one month {> 730 [hours]}
        '''
        if deployment_frequency < 24 and lead_time < 1:
            sdp_classifications_id = 1
        elif (24 < deployment_frequency <= 730) and (1 < lead_time <= 730):
            sdp_classifications_id = 2
        else:
            sdp_classifications_id = 3
        cursor_insert = self.conn.cursor()
        sql_insert = "INSERT INTO SDPClassificationsReleases(IdRelease, IdSDPClassification) VALUES (?, ?);"
        args_insert = (release_id, sdp_classifications_id)
        cursor_insert.execute(sql_insert, args_insert)
        self.conn.commit()



    def update_classifications_metrics_by_name_and_release(self, classifications_metrics_name, release_id, value):
        cursor_delete = self.conn.cursor()
        sql_delete = """ DELETE FROM ClassificationsMetricsReleases 
                            WHERE 
                                IdRelease = ?
                                AND IdClassificationMetric IN (
                                    SELECT Id FROM ClassificationMetrics WHERE Name = ?
                                ); """
        args_delete = (release_id, classifications_metrics_name)
        cursor_delete.execute(sql_delete, args_delete)
        self.conn.commit()

        cursor_insert = self.conn.cursor()
        sql_insert = "INSERT INTO ClassificationsMetricsReleases(IdRelease, IdClassificationMetric, Value) SELECT ?, cm.Id, ? FROM ClassificationMetrics cm WHERE cm.Name = ?"
        args_insert = (release_id, value, classifications_metrics_name)
        cursor_insert.execute(sql_insert, args_insert)
        self.conn.commit()

