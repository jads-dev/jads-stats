<template>
  <v-row>
    <v-col class="text-center" cols="12">
      <v-row justify="center">
        <v-menu v-model="start_date_menu" :close-on-content-click="false" :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
          <template v-slot:activator="{ on, attrs }">
            <v-text-field
              style="max-width: 150px"
              v-model="start_date"
              label="From"
              prepend-icon="mdi-calendar"
              readonly
              v-bind="attrs"
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker v-model="start_date" @input="start_date_menu = false"></v-date-picker>
        </v-menu>
        <v-menu v-model="end_date_menu" :close-on-content-click="false" :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
          <template v-slot:activator="{ on, attrs }">
            <v-text-field style="max-width: 150px" v-model="end_date" label="To" prepend-icon="mdi-calendar" readonly v-bind="attrs" v-on="on"></v-text-field>
          </template>
          <v-date-picker v-model="end_date" @input="end_date_menu = false"></v-date-picker>
        </v-menu>
      </v-row>
    </v-col>
    <v-col class="text-center" cols="12">
      <v-progress-linear v-if="is_loading" indeterminate></v-progress-linear>
      <emotes-bar-chart :chart-data="data_barchart"></emotes-bar-chart>
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
    data_barchart: {},
    data_doughnut: {},
    message_bar: {},
    message_data: [],
    top10_message: [],
    top10_emotes: [],
    top10_reacted: [],
    start_date_menu: false,
    end_date_menu: false,
    start_date: "2020-02-01",
    end_date: "2020-03-01",
    min_date: "",
    max_date: "",
    is_loading: false,
  }),
  methods: {
    fetch_data: async function () {
      this.is_loading = true;

      let message_totals = await this.$dbworker.db.query(`
            with top100 as (
                select emote,  sum(amount) as amount, ROW_NUMBER() over (order by sum(amount) desc ) as sort
                from emote_totals 
                where timestamp between '2020-02-01' and '2020-03-01'
                group by emote
                order by sum(amount) desc
                limit 50
            )

            select t.emote, et.channel, sum(et.amount) as amount
            from top100 as t
            left join emote_totals as et on t.emote = et.emote
            where et.timestamp between '2020-02-01' and '2020-03-01'
            group by t.emote, et.channel
            order by t.sort, t.emote, et.channel
    `);

      let channel_info_array = await this.$dbworker.db.query(`select * from channel_info`);
      let channel_info = {};
      for (var i = 0; i < channel_info_array.length; i++) {
        channel_info[channel_info_array[i].channel_id] = channel_info_array[i];
      }

      let emote_info_array = await this.$dbworker.db.query(`select * from emote_info`);
      let emote_info = {};

      for (var i = 0; i < emote_info_array.length; i++) {
        emote_info[emote_info_array[i].emote_id] = emote_info_array[i];
      }

      let labels_bar = [];
      let dataset_bar = {};

      let last = null;
      message_totals.forEach((element) => {
        if (element.emote != last) {
          last = element.emote;
          labels_bar.push(emote_info[element.emote]["emote_name"]);
        }
        if (!(element.channel in dataset_bar)) dataset_bar[element.channel] = [];
        dataset_bar[element.channel].push(element.amount);
      });

      let data_barchart = {
        labels: labels_bar,
        datasets: [],
      };

      for (const [key, value] of Object.entries(dataset_bar)) {
        data_barchart.datasets.push({
          label: channel_info[key]["channel_name"],
          backgroundColor: channel_info[key]["channel_color"],
          data: value,
          categoryPercentage: 0.9,
          barPercentage: 1,
        });
      }

      this.data_barchart = data_barchart;

      this.is_loading = false;
    },
  },

  mounted: async function () {
    this.fetch_data();

    let dates = await this.$dbworker.db.query("select max(timestamp) as max_date, min(timestamp) as min_date from channel_totals");
    this.min_date = dates[0]["min_date"];
    this.max_date = dates[0]["max_date"];
  },

  watch: {
    start_date: function (n, old) {
      this.fetch_data();
    },
    end_date: function (n, old) {
      this.fetch_data();
    },
  },
};
</script>

