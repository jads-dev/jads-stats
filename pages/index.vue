<template>
  <v-row>
    <v-col class="text-center">
      <all-channels-bar-chart :chart-data="chart_data"></all-channels-bar-chart>
      <!-- {{ $dbworker }} -->
      <!-- {{ message_totals }} -->

      <!-- {{ message_data }} -->
    </v-col>
  </v-row>
</template>



<script>
import AllChannelsBarChart from "~/components/AllChannelsBarChart.vue";
export default {
  data: () => ({
    chart_data: {},
    message_data: [],
  }),

  mounted: async function () {
    // console.log(this.$dbworker);
    let message_totals = await this.$dbworker.db.query(
      `select * 
      from channel_totals 
      where timestamp >= '2020-01-13T17:00:00'
      order by timestamp, channel`
    );

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

      // console.log(dataset_data[element.channel]);
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
      });
    }

    this.chart_data = chart_data;

    this.message_data = message_totals;
  },
};
</script>

