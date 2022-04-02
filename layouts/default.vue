<template>
  <v-app dark>
    <v-navigation-drawer app float>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="text-h6"> Jads Stats </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>

      <v-list dense nav>
        <v-list-item link :to="{ path: '/', query: { start_date: $route.params.start_date, end_date: $route.params.end_date } }">
          <v-list-item-icon>
            <v-icon>mdi-note-outline</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Messages</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item link :to="{ path: '/emotes', query: { start_date: $route.params.start_date, end_date: $route.params.end_date } }">
          <v-list-item-icon>
            <img src="https://cdn.discordapp.com/emojis/318166088863055872.png?size=24" />
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Emotes</v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item link :to="{ path: '/markov_search' }">
          <v-list-item-icon>
            <img src="https://cdn.discordapp.com/avatars/687854633443655814/d220bac5e82f007ea85ea6e1c38911fa.png?size=24" />
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Markov Bot</v-list-item-title>
            <v-list-item-title>(April Fools 2022)</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <v-container>
        <Nuxt />
      </v-container>
    </v-main>
  </v-app>
</template>


<style scoped>
.v-navigation-drawer--close {
  visibility: visible !important;
  transform: translateX(-98%) !important;
}
</style>