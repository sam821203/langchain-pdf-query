import "./assets/main.css";

import { createApp } from "vue";
import { createPinia } from "pinia";
import { library } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

import App from "./App.vue";
import router from "./router";
import {
  faFilePdf,
  faCloudUploadAlt,
  faArrowUp,
} from "@fortawesome/free-solid-svg-icons";

library.add(faFilePdf, faCloudUploadAlt, faArrowUp);

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.component("font-awesome-icon", FontAwesomeIcon);

app.mount("#app");
