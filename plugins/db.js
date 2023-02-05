import Vue from "vue";
import { createDbWorker } from "sql.js-httpvfs";

export default async ({ app, store }, inject) => {
  let data = require("/static/data.json");
  let worker = await createDbWorker(
    [
      {
        from: "jsonconfig",
        configUrl: data.dir_name + "/config.json"
      }
    ],
    "sqlite.worker.js",
    "sql-wasm.wasm"
  );

  inject("dbworker", worker);
};
