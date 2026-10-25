# JOR DOS HEIS 2017 — Table 5.1 Relative Importance by Urban/Rural

Source: https://dosweb.dos.gov.jo/DataBank/household/2017/table5.1.xlsx
(also PDF https://dosweb.dos.gov.jo/DataBank/Expenses/table5.1.pdf)

Published aggregates (row block with Urban/Rural/Kingdom headers ~row 1327):
- Food Commodities % of All Commodities: Urban 32.1285, Rural 37.6696, Kingdom 32.6601
- Nested under Food Commodities before Non-food: Alcohols, Tobacco and Cigarettes, Restaurants and Cafes

To match pack definition used for JOR 2013 (Table 4.25 Food Stuff excl. alcohol/tobacco; restaurants also outside Food Stuff):
food_share = Food Commodities − Alcohols − Tobacco and Cigarettes − Restaurants and Cafes

| cut | Food Comm. | −Alc | −Tob | −Rest | **clean food %** |
|-----|-----------:|-----:|-----:|------:|-----------------:|
| Urban | 32.1285 | 0.0163 | 4.3442 | 1.8556 | **25.91** |
| Rural | 37.6696 | 0 | 5.0866 | 1.1239 | **31.46** |

`estimated_value` empty; arithmetic from same published table only.
