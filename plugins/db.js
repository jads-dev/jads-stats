import Vue from "vue";
import { createDbWorker } from "sql.js-httpvfs";

export default async ({ app, store }, inject) => {
  let data = require("/static/data.json");
  let worker = await createDbWorker(
    [
      {
        from: "inline",
        config: {
          serverMode: "full",
          url: data.filename,
          requestChunkSize: 4096
        }
      }
    ],
    "sqlite.worker.js",
    "sql-wasm.wasm"
  );

  inject("dbworker", worker);
};
