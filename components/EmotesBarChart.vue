<script>
import { Bar, mixins } from "vue-chartjs";
const { reactiveProp } = mixins;
export default {
  extends: Bar,
  mixins: [reactiveProp],
  //   props: ["options"],
  data: () => ({
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        xAxes: [
          {
            stacked: true,
          },
        ],
        yAxes: [
          {
            stacked: true,
          },
        ],
      },
    },
  }),
  mounted() {
    this.addPlugin({
      id: "emote-images",
      afterDraw: (chart) => {
        var ctx = chart.chart.ctx;
        var xAxis = chart.scales["x-axis-0"];
        var yAxis = chart.scales["y-axis-0"];
        xAxis.ticks.forEach((value, index) => {
          var x = xAxis.getPixelForTick(index);
          var image = new Image();
          //   console.log(this.chartData);
          //   (image.src = images[index]), ctx.drawImage(image, x - 12, yAxis.bottom + 10);
        });
      },
    });

    this.renderChart(this.chartData, this.options);
  },
};
</script>

<style>
</style>