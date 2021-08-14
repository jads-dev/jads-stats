<template>
  <v-row>
    <v-col class="text-center">
      <all-channels-bar-chart :chart-data="chart_data"></all-channels-bar-chart>

      <v-textarea v-model="select_query" label="query"> </v-textarea>
      <v-btn @click="fetch_data">run</v-btn>
    </v-col>
  </v-row>
</template>



<script>
import AllChannelsBarChart from "~/components/AllChannelsBarChart.vue";
export default {
  components: { AllChannelsBarChart },
  data: () => ({
    chart_data: {},
    message_data: [],
    select_query: `
      select * 
      from channel_totals 
      where timestamp between '2020-02-01' and '2020-03-01'
      order by timestamp, channel`,
  }),
  methods: {
    fetch_data: async function () {
      let message_totals = await this.$dbworker.db.query(this.select_query);

      let channel_info_array = await this.$dbworker.db.query(
        `select * from channel_info`
      );

      let channel_info = {};

      for (var i = 0; i < channel_info_array.length; i++) {
        channel_info[channel_info_array[i].channel_id] = channel_info_array[i];
      }

      let labels = [];
      let dataset_data = {};

      let last_timestamp = "";
      message_totals.forEach((element) => {
        if (element.timestamp != last_timestamp) {
          last_timestamp = element.timestamp;
          labels.push(element.timestamp);
        }
        if (!(element.channel in dataset_data))
          dataset_data[element.channel] = [];
        dataset_data[element.channel].push(element.message_count);
      });

      let chart_data = {
        labels: labels,
        datasets: [],
      };

      for (const [key, value] of Object.entries(dataset_data)) {
        chart_data.datasets.push({
          label: channel_info[key]["channel_name"],
          backgroundColor: channel_info[key]["channel_color"],
          data: value,
          categoryPercentage: 1,
          barPercentage: 1,
        });
      }

      this.chart_data = chart_data;

      this.message_data = message_totals;
    },
  },

  mounted: async function () {
    this.fetch_data();
  },
};
</script>

