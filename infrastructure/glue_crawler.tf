resource "aws_glue_catalog_database" "crawler_db" {
    name = "desafio_crawler_db"
}

resource "aws_glue_crawler" "crawler" {
    database_name = aws_glue_catalog_database.crawler_db.name
    name = "desafio_crawler"
    role = "DesMod1GlueCrawlerRole"

    s3_target {
      path = "s3://datalake-felipeschreiber-desafio/staging-zone/rais/"
    }

    configuration = <<EOF
    {
        "Version": 1.0,
        "Grouping": {
            "TableGroupingPolicy": "CombineCompatibleSchemas"
        }
    }
    EOF

    tags = {
        CURSO     = "EDC"
        MODULO    = "1"
        USE_CASE  = "DESAFIO"
    }

}