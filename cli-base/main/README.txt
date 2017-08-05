Main parameters:

    --oname     'Organization Name'       - e.g., Panoptesec-DAM
    --oid        OrganizationID
    --dename    'Detrimental Event Name'  - e.g., 'Control Station Hacking Threat'
    --deid       DetEventID               - e.g., A7 for 'Control Station Hacking Threat'

In terms of countermeasure combinations:
    --all                                 - default, such that all MAs associated to the DE will be combined
    --avg                                 - just those MAs with a RORI value higher than the average RORI value will be combined
    --treshold     Value                  - just those MAs with a RORI value above the threshold will be combined
    --listofma      'listofMA'            - combine those MAs whose ID is given as parameter.
Filtrage options:
     --BestMA   		- Display only the best Mitigation Action from individual RORI evaluation
     --BestRP	  		- Display only the best Response Plan from the combined RORI evaluation
Output options:
     --json           - Generate a JSON file with the results (to be used only with BestMA or BestRP options)

Examples:

1/    python rfia-cli.pyc --oname 'Panoptesec-DAM' --dename 'Control Station Hacking Threat'

2/    python rfia-cli.pyc --oname 'Panoptesec-DAM' --dename 'Control Station Hacking Threat' --threshold 300

3/    python rfia-cli.pyc --oname 'Panoptesec-DAM' --deid A7 --avg
