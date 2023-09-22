# Bus-interchange-hk - Add your own bus interchange guide
This is a guide that guides you to add any bus stop to the program. This guide involves a small
amount of knowledge in computer programming. Please follow all steps closely.

## Requirements
- A web browser (preferrably with a JSON formatter such as Firefox)
- An active internet connection
- A bit of patience

[][]

## Getting the Stop IDs
Bus companies represent real-life stops as stop IDs. KMB uses more of them than Citybus. For
example, KMB registers 9 of them for Cross Harbour Tunnel Bus Interchange (Southbound), each for
one "bus stop pole", while Citybus only uses 3, one for a different section of the interchange.

A helpful rule of thumb is that, if there is a physical object designated for a group of routes,
then there is a separate stop ID for KMB.
On the other hand, if two groups of stops require extensive walking between them, or if they are in
separated roads (e.g. Tsing Shan Road and Tuen Mun Highway in Tuen Mun Highway BBI), they would
have separate stop IDs.

To make your interchange complete, you must identify at least one route for each stop ID. Note that
KMB and Citybus stop IDs will never overlap, and you have to identify all stop IDs individually for
each company.

KMB uses hexadecimals of length 16 (e.g. 123456789ABCDEF0) while Citybus uses 6-digit decimal
numbers (e.g. 001234) to represent stop IDs.

### KMB
Visit this URL

https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{route}/{direction}/1

https://data.etabus.gov.hk/v1/transport/kmb/stop/{id}

### CTB
https://rt.data.gov.hk/v2/transport/citybus/route-stop/CTB/{route}/{direction}/

https://rt.data.gov.hk/v2/transport/citybus/stop/{id}


# Troubleshooting
Q: A jointly operated route is shown as operated by only one company
A: Check if the other company's stop ID is correctly added below.

Q: A route is missing.
A: Check if the stop ID(s) are correctly added below.
