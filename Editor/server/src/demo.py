from tools import settings
from features import executor

# dataModel = data_model.make_datamodel()
# print(dataModel)

sql = """
    WITH cte AS (
        SELECT tab0.col0_1, tab0.col0_2, tab00.col00_2 FROM tab0
        JOIN tab00 USING (tab0_id))
    SELECT 
        cte.col00_2,
        tab10.col10_2,
        (SELECT count(tab20.col20_2) FROM tab20)
    --FROM tree
    --join cte ON tree.col_1 = cte.col0_1
    FROM cte 
    join tab ON tab.col_1 = cte.col0_1
    JOIN tab1 USING (tab_id)
    JOIN tab10 USING (tab1_id)"""

# executor.execute(sql)

if __name__ == '__main__':
    try:
        s = settings._load()
    except Exception as e:

        ...


