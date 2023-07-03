# Test Harness For Solr BooleanClause generation

Contains some python scripts to make multiple queries against Solr, collect
some statistics, and do some basic reporting on those statistics.  One 
primary value of this is to view the relationship between the sorts of
queries you make against your Solr instance and the affect that has on
the performance of your Solr instance and also on the automatic generation
of `BooleanClause`s, particularly by use of the `dismax` and `edismax`
query parsers.  


As of Solr 8.x, Solr typically enforces a 1024 boolean clause limit, so this can also help tune your settings.

## Usage

    $ pip install --user requirements.txt

This will install the `requests` and `pandas` libraries; if you prefer, you 
can use some other means of installing these so they're available to your 
python interpreter.

1. Run the queries and defaults from the 'author' directory against Solr 4

    $ ./queries.py

Will run a (somewhat) silly set of default queries against a Solr collection
named `_default` running on `localhost`, and store the actual responses in the
`json` subdirectory, and a CSV file in `results`.  See below for a breakdown of
the contents of the CSV file.

2. Run a custom set of queries against a specified Solr host and collection

    $ ./queries.py -c trlnbib -t author --query-dir author solr_4

This loads `params.json` and `queries.txt` from the `author` subdirectory.  The
former specifies the default parameters to use with each query, and the latter
specifies, one per line, the values of the `q` Solr parameter to use in running
the test.  Solr JSON responses and test results will be stored as above,
however the 'test_type' parameter in the CSV file (as well as its name) will
reflect the value of the `-t` parameter (in this case, `author`).

## CSV Format

`host,test_number,test_type,querylen,result_count,time,solr_qtime,num_clauses,query`

 - `host` - the Solr host the query was run against
 - `test_number` - the value of the `-n` parameter (default: 1)
 - `test_type` - the value of the `-t` parameter (default: 'default')
 - `querylen` - a guess about the number of terms in the query
 - `result_count` - the number of results matching the query (from Solr)
 - `time` - the amount of time it took to make the query and receive the results
            (so, what it felt like for the client)
 - `solr_qtime` - the `QTime` value found in the Solr response.
 - `num_clauses` - a count of the number of boolean clauses in the query
 - `query` - the value of the `q` parameter passed to solr (minus any prefix, see below)

`num_clauses` is determined by looking for `|` (pipe) characters in the
`parsedquery` attribute of the `debug` value in the Solr response (`debug` is
always set to `true` by this tool).  If q.op is something else, edit the code
as appropriate.

This format allows us to aggregate results in a somewhat useful way (especially
when comparing the performance of different Solr configurations or versions
running on different hosts).  Your purposes may be different, so feel free to change the output as you see fit for the analysis you want to perform.

## `queries.py` usage

The range of arguments you can pass to the script is somewhat large, to provide
a measure of flexibility in generating different test scenarios.  Run `./queries.py -h` to get a general breakdown.

`-n` -- it is expected you may run the tests a number of times, so you can provide this to number your tests.  It defaults to 1.

`-c` -- the `collection` name to run queries against.  Not used if `-u` is specified, default value: `default`.

`--query-dir` - a directory to be scanned for `queries.txt` and `params.json` files. These files are used as the value of `--query-file` and `--default-query` if present.  Either or both can be overriden by the explict use of their companion argument.

`--query-file` - a file containing the `q` parameter of the queries to be run aspart of the test, one per line.

`--default-query` - a JSON file containing the other Solr query parameters you
want to specify for each query that's run, e.g. `{ "fq":
"some_field:filter_value", "defType": "lucene" }` will add
`&fq=some_field:filter_value&defType=lucene` to each Solr query string.

The special parameter `:_prefix` can be added to this file to add a prefix to
each query, which is especially useful for long and complex `edismax` and
`dismax` queries, e.g.  `{ ":_prefix": "{!edismax
qf=$my_qf_defined_in_solrconfig_defaults}"}` will add the value at the
beginning of the queries in `queries.txt` (or the default queries, if you don't
have a `queries.txt`).  Other than prepending to the `q` parameter, this
attribute will not be passed to Solr, however.

Since `debug=true` is essential, it is automatically added to the default
parameters

`-u` - specify the _complete_ URL to use for queries, including the path to the
query handler you want to use. Mostly useful when you're using `https` or some
port other than `8983`; overrides any value provided for `host` and
`collection`. Example:
`https://my-solr-behind-a-proxy.edu/solr/myneatcollection/select`
The value of `host` in the output will be derived from this parameter (`urllib.urlparse.parse(url).netloc`) if its set.

The final positional parameter passed to the program is the hostname.  Unless `-u` is set, the URL to be used for queries will be the pattern `http://{hostname}:8983/solr/{collection}/select`

## CSV Filenames

In an attempt to avoid collisions between different types of test, the output
filenames for the CSV files are derived from the hostname, the value of `-n`,
the value of the `-t` parameter, e.g.
`results/{host}-test-{n}-{test_type}.csv`.  Runs where all three of these
parameters match the result of a previous test run will *overwrite* the file.

## Analysis

Some low-level basic analysis, via `pandas`, can be done on the output by
running the `analyze.py` script; this expects to find CSV files of the form
output by `queries.py` in the `results` directory, and aggregates _all_ such
files together by `hostname`, `test_type`, and `querylen` (number of terms) to
generate some simple output that lets you quickly see how query length affects
the number of boolean clauses generated, as well as performance.  Otherwise,
feel free to regard it as something you can build your own more complex 
analyses from.

