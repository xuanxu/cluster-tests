from astroquery.utils.tap.core import Tap

def query_tap_table(tap_url, query):
    tap_service = Tap(url=tap_url)
    result = tap_service.launch_job(query)
    return result.get_results()

def query_esa_cluster_table(query):
    esa_cluster_tap_url = "https://csa.esac.esa.int/csa-sl-tap/data"
    return query_tap_table(esa_cluster_tap_url, query)

# Example usage:
# query = "SELECT * FROM cluster_source_table LIMIT 10"
# results = query_esa_cluster_table(query)
# print(results)
