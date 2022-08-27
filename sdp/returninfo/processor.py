import csv
import os
from datetime import datetime

from loaddata.gql.db_repofiles import DbRepoFiles
from loaddata.gql.db_repolanguages import DbRepoLanguages
from loaddata.gql.gql_db_mergedpullrequests import GQLdbMergedPullrequests
from loaddata.gql.gql_db_releases import GQLdbReleases
from loaddata.gql.gql_db_repos import GQLdbRepos
from returninfo.db_processor import DbProcessor

import numpy as np


class Processor:
    def __init__(self, logger, conn):
        self.logger = logger
        self.conn = conn

    def _log_run(self, function_name):
        self.logger.info("     *) {}".format(function_name))

    def _dates_diff_in_hours(self, date1, date2):
        diff_dt = date1 - date2
        return abs(diff_dt.days * 24 + diff_dt.seconds // 3600)

    def _releases_dates_diff_in_hours(self, release_date, processed_releases_dates):
        ts_list = []
        ts_list.extend(processed_releases_dates)
        ts_list.append(release_date)
        dif_list = []
        for i in range(len(ts_list) - 1):
            total_diff_in_hours = self._dates_diff_in_hours(ts_list[i], ts_list[i + 1])
            dif_list.append(total_diff_in_hours)
        return np.mean(dif_list)

    def _get_total_diff_dt_release_pullrequestscommit_in_hours(self, release_date, release_pr_commits):
        dif_list = []
        for release_pr_commit in release_pr_commits:
            release_pr_commit_dt = datetime.strptime(release_pr_commit[2], '%Y-%m-%dT%H:%M:%SZ')
            total_diff_in_hours = self._dates_diff_in_hours(release_date, release_pr_commit_dt)
            dif_list.append(total_diff_in_hours)
        return np.mean(dif_list)

    def _set_metric_values(self, db_processor, repo_id):
        gql_releases = GQLdbReleases(self.logger, self.conn, "     process_releases", "", repo_id, "", "", False)
        releases = gql_releases.list_by_repo_id(repo_id)

        db_repo_files = DbRepoFiles(self.conn, "", repo_id, "", "", "")
        gql_db_pr = GQLdbMergedPullrequests(self.logger, self.conn, "     process_mergedpullrequests", "", repo_id, "", "", False)
        processed_releases_dates = []
        for release in releases:
            release_id = release[0]

            # set worst default values in hours before calculate them for each release
            deployment_frequency = 750  # more than 1 month in hours
            lead_time = 750  # more than 1 month in hours

            release_date = datetime.strptime(release[6], '%Y-%m-%dT%H:%M:%SZ')
            if len(processed_releases_dates) > 0:
                deployment_frequency = self._releases_dates_diff_in_hours(release_date, processed_releases_dates)
            db_processor.update_classifications_metrics_by_name_and_release("Deployment frequency", release_id, deployment_frequency)
            processed_releases_dates.append(release_date)

            first_date = processed_releases_dates[len(processed_releases_dates)-2] if len(processed_releases_dates) > 1 else datetime.min
            final_date = processed_releases_dates[len(processed_releases_dates)-1]
            release_pr_commits = gql_db_pr.list_with_latest_commit_by_repo_and_dates(repo_id, first_date, final_date)
            if len(release_pr_commits) > 0:
                lead_time = self._get_total_diff_dt_release_pullrequestscommit_in_hours(release_date, release_pr_commits)
            db_processor.update_classifications_metrics_by_name_and_release("Lead Time", release_id, lead_time)

            db_processor.update_classifications_metrics_by_name_and_release("Commits", release_id, len(release_pr_commits))

            db_processor.update_sdp_classifications(deployment_frequency, lead_time, release_id)

            has_ci_tool = db_repo_files.has_ci_tool(release_date)
            db_processor.update_classifications_metrics_by_name_and_release("CI usage", release_id, has_ci_tool)
            has_cd_tool = db_repo_files.has_cd_tool(release_date)
            db_processor.update_classifications_metrics_by_name_and_release("CD usage", release_id, has_cd_tool)

    def process(self, output_path):
        if os.path.exists(output_path):
            self._log_run("Removing Output file for a new run...")
            os.remove(output_path)
        else:
            self._log_run("No previous Output file found, creating a brand new one...")
        self._log_run("Start writing results.csv...")
        f = open(output_path, 'w')
        writer = csv.writer(f)
        header = ['Id_Repo', 'Repo_Name', 'Repo_owner', 'Main_Language', 'First_Date_CiCd',	'Min_Release_Date', 'Max_Release_Date', 'Delta_Days_First_Release_Until_CiCd', 'Delta_Days_Last_Release_After_CiCd', 'Count_Releases_Before_DateCiCd', 'Count_Releases_After_DateCiCd', 'Count_Releases_Before_CiCd_Low_Performers', 'Count_Releases_Before_CiCd_Medium_Performers', 'Count_Releases_Before_CiCd_High_Performers', 'Count_Releases_After_CiCd_Low_Performers', 'Count_Releases_After_CiCd_Medium_Performers', 'Count_Releases_After_CiCd_High_Performers']
        writer.writerow(header)

        gql_db_repos = GQLdbRepos(self.logger, self.conn, "     process_repos", "", 0, 0, False)
        repos = gql_db_repos.list_all_with_data()
        for repo in repos:
            repo_id = str(repo[0])
            repo_name = repo[1]
            repo_owner = repo[2]
            self._log_run(f"Setting metric values for Repo id:{repo_id}, repo:{repo_owner}/{repo_name} ...")
            db_processor = DbProcessor(self.conn)
            self._set_metric_values(db_processor, repo_id)

            self._log_run(f"Writing csv results for Repo id:{repo_id}, repo:{repo_owner}/{repo_name} ...")
            db_repo_languages = DbRepoLanguages(self.conn, None, repo_id, repo_name, repo_owner)
            db_repo_lang = db_repo_languages.get_main_language_by_id_repo(repo_id)
            repo_main_language = "None"
            if db_repo_lang is not None:
                repo_main_language = db_repo_lang[0]

            gql_db_releases = GQLdbReleases(self.logger, self.conn, "     get_releases_min_max_dates", "", repo_id, repo_name, repo_owner, False)
            release_dates = gql_db_releases.get_min_max_date_by_repo_id(repo_id)
            min_release_date = datetime.strptime(release_dates[0], '%Y-%m-%dT%H:%M:%SZ')
            max_release_date = datetime.strptime(release_dates[1], '%Y-%m-%dT%H:%M:%SZ')

            db_repo_files = DbRepoFiles(self.conn, "", repo_id, repo_name, repo_owner, "")
            delta_days_first_release_until_cicd = 0
            delta_days_last_release_after_cicd = 0
            repo_first_date_cicd = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            date_cicd = db_repo_files.get_date_cicd_by_id_repo(repo_id)
            if date_cicd is not None:
                repo_first_date_cicd = datetime.strptime(date_cicd, '%Y-%m-%dT%H:%M:%SZ')
                delta_days_first_release_until_cicd = (repo_first_date_cicd - min_release_date).days
                delta_days_last_release_after_cicd = (max_release_date - repo_first_date_cicd).days

            counts_release = gql_db_releases.get_counts_by_repo_id_and_date(repo_id, repo_first_date_cicd)
            count_releases_before_date = counts_release[0]
            count_releases_after_date = counts_release[1]

            count_releases_before_cicd_low_performers = 0
            count_releases_before_cicd_medium_performers = 0
            count_releases_before_cicd_high_performers = 0
            count_releases_after_cicd_low_performers = 0
            count_releases_after_cicd_medium_performers = 0
            count_releases_after_cicd_high_performers = 0
            return_info_datas = gql_db_repos.list_returninfo_data_by_repo_id_and_release_date(repo_id, repo_first_date_cicd)
            for return_data in return_info_datas:
                rd_order_id = return_data[0]
                rd_count = return_data[1]
                rd_classification = return_data[2]
                if rd_order_id == 0:
                    if rd_classification == 'Low Performers': count_releases_before_cicd_low_performers = rd_count
                    elif rd_classification == 'Medium Performers': count_releases_before_cicd_medium_performers = rd_count
                    elif rd_classification == 'High Performers': count_releases_before_cicd_high_performers = rd_count
                else:
                    if rd_classification == 'Low Performers': count_releases_after_cicd_low_performers = rd_count
                    elif rd_classification == 'Medium Performers': count_releases_after_cicd_medium_performers = rd_count
                    elif rd_classification == 'High Performers': count_releases_after_cicd_high_performers = rd_count

            writer.writerow([repo_id, repo_name, repo_owner, repo_main_language, repo_first_date_cicd, min_release_date, max_release_date, delta_days_first_release_until_cicd, delta_days_last_release_after_cicd, count_releases_before_date, count_releases_after_date, count_releases_before_cicd_low_performers, count_releases_before_cicd_medium_performers, count_releases_before_cicd_high_performers, count_releases_after_cicd_low_performers, count_releases_after_cicd_medium_performers, count_releases_after_cicd_high_performers])

        f.close()
        self._log_run("results.csv wrote successfully")
