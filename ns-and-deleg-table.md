~~~
Assumptions: a DELEG-aware server and a query that would lead to a delegation

If the query has the DE EDNS0 flag set:
  If the auth has just NS records:
    Return NS records in the Authority section
  If the auth has just DELEG records:
    Return DELEG records in the Authority section
  If the auth has both NS and DELEG records:
    Option A: Return only DELEG records in the Authority section
    Option B: Return both DELEG and NS records in the Authority section


If the query has the DE EDNS0 flag clear:
  If the auth has just NS records:
    Return NS records in the Authority section
  If the auth has just DELEG records:
    Option C: Set RCODE=NOERROR and return nothing in the Authority section (sort of like NODATA)
    Option D: Set RCODE=NXDOMAIN and return nothing in the Authority section
    Option G: Set RCODE=SERVFAIL and return nothing in the Authority section
    Option H: Return NS and glue records in the Authority section synthesized from the DELEG records
  If the auth has both NS and DELEG records:
    Option E: Return only NS records in the Authority section
    Option F: Return both DELEG and NS records in the Authority section
~~~
