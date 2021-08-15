<template>
  <v-row>
    <v-col class="text-center" cols="12">
      <div>
        <v-btn x-small @click="change_date('start', -30)"> -1 month </v-btn>
        <v-btn x-small @click="change_date('start', -7)"> -1 week </v-btn>
        <v-btn x-small @click="change_date('start', -1)"> -1 day </v-btn> Start: {{ start_date }}
        <v-btn x-small @click="change_date('start', 1)"> +1 day </v-btn>
        <v-btn x-small @click="change_date('start', 7)"> +1 week </v-btn>
        <v-btn x-small @click="change_date('start', 30)"> +1 month </v-btn>
      </div>
      <div>
        <v-btn x-small @click="change_date('end', -30)"> -1 month </v-btn>
        <v-btn x-small @click="change_date('end', -7)"> -1 week </v-btn>
        <v-btn x-small @click="change_date('end', -1)"> -1 day </v-btn> End: {{ end_date }}
        <v-btn x-small @click="change_date('end', 1)"> +1 day </v-btn>
        <v-btn x-small @click="change_date('end', 7)"> +1 week </v-btn>
        <v-btn x-small @click="change_date('end', 30)"> +1 month </v-btn>
      </div>
    </v-col>
    <v-col class="text-center" cols="12">
      <all-channels-bar-chart :chart-data="data_barchart"></all-channels-bar-chart>
    </v-col>
    <v-col class="text-center" cols="3">
      <all-channel-doughnut-chart :chart-data="data_doughnut"></all-channel-doughnut-chart>
    </v-col>
    <v-col class="text-center" cols="3">
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
    <v-col class="text-center" cols="3">
      Top 10 most messages with emotes
      <v-simple-table dense>
        <thead>
          <tr>
            <th class="text-right">Messages</th>
            <th class="text-left">User</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in top10_emotes" :key="`t10m_${user.user}`">
            <td class="text-right">{{ user.emote_count }}</td>
            <td class="text-left">{{ user.username }}</td>
          </tr>
        </tbody>
      </v-simple-table>
    </v-col>
    <v-col class="text-center" cols="3">
      Top 10 most reacted to
      <v-simple-table dense>
        <thead>
          <tr>
            <th class="text-right">Messages</th>
            <th class="text-left">User</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in top10_reacted" :key="`t10m_${user.user}`">
            <td class="text-right">{{ user.reaction_count }}</td>
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
    top10_emotes: [],
    top10_reacted: [],
    start_date: "2020-01-01",
    end_date: "2022-03-01",
  }),
  methods: {
    fetch_data: async function () {
      let message_totals = await this.$dbworker.db.query(`
          select timestamp, channel, sum(message_count) as message_count, sum(emote_count) as emote_count, sum(reaction_count) as reaction_count
          from channel_totals 
          where timestamp between '${this.start_date}' and '${this.end_date}'
          group by timestamp, channel
          order by timestamp, channel
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

      console.log(data_doughnut);
      this.data_barchart = data_barchart;
      this.data_doughnut = data_doughnut;

      let top10_message = await this.$dbworker.db.query(`
          select user, username, sum(message_count) as message_count
          from channel_totals  as ct 
          left join user_info as ui on ui.user_id = ct.user
          where timestamp between '${this.start_date}' and '${this.end_date}'
          group by user, username
          order by sum(message_count) desc
          limit 10
    `);

      let top10_emotes = await this.$dbworker.db.query(`
          select user, username, sum(emote_count) as emote_count
          from channel_totals  as ct 
          left join user_info as ui on ui.user_id = ct.user
          where timestamp between '${this.start_date}' and '${this.end_date}'
          group by user, username
          order by sum(emote_count) desc
          limit 10
    `);

      let top10_reacted = await this.$dbworker.db.query(`
          select user, username, sum(reaction_count) as reaction_count
          from channel_totals  as ct 
          left join user_info as ui on ui.user_id = ct.user
          where timestamp between '${this.start_date}' and '${this.end_date}'
          group by user, username
          order by sum(reaction_count) desc
          limit 10
    `);

      this.top10_message = top10_message;
      this.top10_emotes = top10_emotes;
      this.top10_reacted = top10_reacted;
    },

    change_date: function (date_type, amount) {
      let date_str = "";
      if (date_type == "start") date_str = this.start_date.replaceAll("-", "/");
      else date_str = this.end_date.replaceAll("-", "/");

      let new_date = new Date(date_str);

      if (amount >= 30) new_date.setMonth(new_date.getMonth() + 1);
      else if (amount <= -30) new_date.setMonth(new_date.getMonth() - 1);
      else new_date.setDate(new_date.getDate() + amount);

      let new_date_str = new_date.toISOString().slice(0, 10);

      if (date_type == "start") this.start_date = new_date_str;
      else this.end_date = new_date_str;
    },
  },

  mounted: async function () {
    this.fetch_data();
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

