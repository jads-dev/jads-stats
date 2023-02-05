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
      <all-channels-bar-chart :chart-data="data_barchart"></all-channels-bar-chart>
    </v-col>
    <v-col class="text-center" cols="12" md="3">
      <all-channel-doughnut-chart :chart-data="data_doughnut"></all-channel-doughnut-chart>
    </v-col>
    <v-col class="text-center" cols="12" md="3">
      Top 10 most messages
      <v-simple-table dense>
        <thead>
          <tr>
            <th class="text-right">Messages</th>
            <th class="text-left">User</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in top10_message" :key="`t10m_${user.user}`">
            <td class="text-right">{{ user.message_count }}</td>
            <td class="text-left">{{ user.username }}</td>
          </tr>
        </tbody>
      </v-simple-table>
    </v-col>
    <v-col class="text-center" cols="12" md="3">
      Top 10 most average poster
      <v-simple-table dense>
        <thead>
          <tr>
            <th class="text-right">Messages</th>
            <th class="text-left">User</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in top10_average_poster" :key="`t10m_${user.user}`">
            <td class="text-right">{{ user.messages }}</td>
            <td class="text-left">{{ user.username }}</td>
          </tr>
        </tbody>
      </v-simple-table>
    </v-col>
    <v-col class="text-center" cols="12" md="3">
      Top 10 most messages reacted to
      <v-simple-table dense>
        <thead>
          <tr>
            <th class="text-right">Messages</th>
            <th class="text-left">User</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in top10_reacted" :key="`t10m_${user.user}`">
            <td class="text-right">{{ user.react_percent }}</td>
            <td class="text-left">{{ user.username }}</td>
          </tr>
        </tbody>
      </v-simple-table>
    </v-col>
  </v-row>
</template>



<script>
import AllChannelDoughnutChart from "~/components/AllChannelDoughnutChart.vue";
import AllChannelsBarChart from "~/components/AllChannelsBarChart.vue";

import data from "/static/data.json"

function parseDate(date) {
  const parsed = Date.parse(date);
  if (!isNaN(parsed)) {
    return parsed;
  }

  return Date.parse(date.replace(/-/g, "/").replace(/[a-z]+/gi, " "));
}

export default {
  components: { AllChannelsBarChart, AllChannelDoughnutChart },
  data: () => ({
    data_barchart: {},
    data_doughnut: {},
    message_bar: {},
    message_data: [],
    top10_message: [],
    top10_average_poster: [],
    top10_reacted: [],
    start_date_menu: false,
    end_date_menu: false,
    default_start_date: data.start_date,
    default_end_date: data.end_date,
    min_date: "",
    max_date: "",
    is_loading: false,
  }),
  methods: {
    fetch_data: async function () {
      this.is_loading = true;

      let message_totals = await this.$dbworker.db.query(`
          with c as (
            select distinct timestamp, channel_id
            from channel_totals, channel_info
            where timestamp between '${this.start_date}' and '${this.end_date}'
          )

          select c.timestamp, channel_id as channel, ifnull(sum(message_count),0) as message_count, ifnull(sum(emote_count),0) as emote_count, ifnull(sum(reaction_count),0) as reaction_count
          from c
          left join channel_totals as ct on ct.timestamp = c.timestamp and ct.channel = c.channel_id 
          where c.timestamp between '${this.start_date}' and '${this.end_date}'
          group by c.timestamp, channel_id
          order by c.timestamp, channel_id
    `);

      let channel_info_array = await this.$dbworker.db.query(`select * from channel_info`);

      let channel_info = {};

      for (var i = 0; i < channel_info_array.length; i++) {
        channel_info[channel_info_array[i].channel_id] = channel_info_array[i];
      }

      let labels_bar = [];
      let dataset_bar = {};

      let last_timestamp = "";
      message_totals.forEach((element) => {
        if (element.timestamp != last_timestamp) {
          last_timestamp = element.timestamp;
          labels_bar.push(element.timestamp);
        }
        if (!(element.channel in dataset_bar)) dataset_bar[element.channel] = [];
        dataset_bar[element.channel].push(element.message_count);
      });

      let data_barchart = {
        labels: labels_bar,
        datasets: [],
      };

      let labels_doughtnut = [];
      let dateset_doughnut_data = [];
      let dateset_doughnut_colors = [];

      for (const [key, value] of Object.entries(dataset_bar)) {
        data_barchart.datasets.push({
          label: channel_info[key]["channel_name"],
          backgroundColor: channel_info[key]["channel_color"],
          data: value,
          categoryPercentage: 1,
          barPercentage: 1,
        });

        labels_doughtnut.push(channel_info[key]["channel_name"]);
        dateset_doughnut_data.push(value.reduce((a, b) => a + b, 0));
        dateset_doughnut_colors.push(channel_info[key]["channel_color"]);
      }

      let data_doughnut = {
        labels: labels_doughtnut,
        datasets: [{ data: dateset_doughnut_data, backgroundColor: dateset_doughnut_colors }],
      };

      this.data_barchart = data_barchart;
      this.data_doughnut = data_doughnut;

      let top10_message = await this.$dbworker.db.query(`
          select user, username, sum(message_count) as message_count
          from channel_user_totals as ct 
          left join user_info as ui on ui.user_id = ct.user
          where timestamp between '${this.start_date}' and '${this.end_date}'
          group by user, username
          order by sum(message_count) desc
          limit 10
    `);

      let top10_average_poster = await this.$dbworker.db.query(`
          with avg as ( select sum(message_count) / count(distinct user) as avg
            from channel_user_totals as ct 
            left join user_info as ui on ui.user_id = ct.user
            where timestamp between '${this.start_date}' and '${this.end_date}'
          )

          select user, username, sum(message_count) as  messages
          from channel_user_totals as ct, avg
          left join user_info as ui on ui.user_id = ct.user
          where timestamp between '${this.start_date}' and '${this.end_date}'
          group by user, username
          order by abs(avg.avg - sum(message_count)) asc
          limit 10
    `);

      let top10_reacted = await this.$dbworker.db.query(`
          select user, username, cast(round(cast(sum(reaction_count) as real) / sum(message_count), 3) * 100 as text) || '%' as react_percent
          from channel_user_totals as ct 
          left join user_info as ui on ui.user_id = ct.user
          where timestamp between '${this.start_date}' and '${this.end_date}'
          group by user, username
          having sum(reaction_count) > 100
          order by cast(sum(reaction_count) as real) / sum(message_count) desc
          limit 10
    `);

      this.top10_message = top10_message;
      this.top10_average_poster = top10_average_poster;
      this.top10_reacted = top10_reacted;
      this.is_loading = false;
    },
  },

  computed: {
    start_date: {
      get() {
        return this.$route.query.start_date || this.default_start_date;
      },
      set(value) {
        this.$router.replace({
          query: {
            ...this.$route.query,
            start_date: value,
          },
        });
      },
    },
    end_date: {
      get() {
        return this.$route.query.end_date || this.default_end_date;
      },
      set(value) {
        this.$router.replace({
          query: {
            ...this.$route.query,
            end_date: value,
          },
        });
      },
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
  head() {
    return {
      title: "Messages",
      meta: [
        // hid is used as unique identifier. Do not use `vmid` for it as it will not work
        {
          hid: "description",
          name: "description",
          content: "Stats for JADS message counts",
        },
      ],
    };
  },
};
</script>

