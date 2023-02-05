<template>
  <v-row>
    <v-col class="text-center" cols="12">
      <v-row justify="center">
        <v-textarea auto-grow v-model="query"></v-textarea>
      </v-row>
      <v-row justify="center">
        <v-btn @click="fetch_data()">Run</v-btn>
      </v-row>
      <v-row justify="center">
        <v-data-table dense hide-default-footer disable-pagination :items="data" :headers="headers" :loading="is_loading"></v-data-table>
      </v-row>
    </v-col>
  </v-row>
</template>



<script>
import EmotesBarChart from "../components/EmotesBarChart.vue";

function parseDate(date) {
  const parsed = Date.parse(date);
  if (!isNaN(parsed)) {
    return parsed;
  }

  return Date.parse(date.replace(/-/g, "/").replace(/[a-z]+/gi, " "));
}

export default {
  components: { EmotesBarChart },
  data: () => ({
    query: `
    select user, ei.emote_name, sum(amount)
    from emote_totals_breakdown as eub
    left join emote_info as ei on ei.emote_id = eub.emote
    where user = 338344227719348224
    group by user, ei.emote_name
    order by sum(amount) desc
   `,
    data: [],
    is_loading: false,
  }),
  methods: {
    fetch_data: async function () {
      this.is_loading = true;
      this.data = await this.$dbworker.db.query(this.query);
      this.is_loading = false;
    },
  },

  computed: {
    headers: {
      get() {
        let headers = [];
        if (this.data.length > 0) {
          Object.keys(this.data[0]).forEach((element) => {
            headers.push({ text: element, value: element });
          });
        }
        return headers;
      },
      set(value) {},
    },
  },

  head() {
    return {
      title: "Query",
      meta: [
        // hid is used as unique identifier. Do not use `vmid` for it as it will not work
        {
          hid: "description",
          name: "description",
          content: "query page",
        },
      ],
    };
  },
};
</script>

