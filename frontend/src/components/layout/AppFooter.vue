<template>
  <footer class="bg-gray-900 text-gray-300 mt-16">
    <div class="container mx-auto px-4 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- About -->
        <div>
          <h3 class="text-white text-lg font-semibold mb-4">
            {{ $t("footer.about") }}
          </h3>
          <p class="text-sm leading-relaxed">
            {{ $t("footer.aboutText") }}
          </p>
        </div>

        <!-- Quick links -->
        <div>
          <h3 class="text-white text-lg font-semibold mb-4">
            {{ $t("footer.quickLinks") }}
          </h3>
          <ul class="space-y-2 text-sm">
            <li>
              <router-link to="/articles" class="hover:text-white">
                {{ $t("nav.articles") }}
              </router-link>
            </li>
            <li>
              <router-link to="/books" class="hover:text-white">
                {{ $t("nav.books") }}
              </router-link>
            </li>
            <li>
              <router-link to="/dissertations" class="hover:text-white">
                {{ $t("nav.dissertations") }}
              </router-link>
            </li>
            <li>
              <router-link to="/search" class="hover:text-white">
                {{ $t("nav.search") }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Support -->
        <div>
          <h3 class="text-white text-lg font-semibold mb-4">
            {{ $t("footer.support") }}
          </h3>
          <ul class="space-y-2 text-sm">
            <li>
              <a href="#" class="hover:text-white">{{ $t("footer.help") }}</a>
            </li>
            <li>
              <a href="#" class="hover:text-white">{{
                $t("footer.contact")
              }}</a>
            </li>
            <li>
              <a href="#" class="hover:text-white">{{ $t("footer.faq") }}</a>
            </li>
          </ul>
        </div>

        <!-- Contact -->
        <div>
          <h3 class="text-white text-lg font-semibold mb-4">
            {{ $t("footer.contact") }}
          </h3>
          <ul class="space-y-2 text-sm">
            <li>
              <a href="mailto:library@smu.edu.tm" class="hover:text-white">
                library@smu.edu.tm
              </a>
            </li>
            <li>
              <a href="tel:+99312123456" class="hover:text-white">
                +993 (12) 12-34-56
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="border-t border-gray-800 mt-8 pt-8 text-sm text-center">
        <p>
          &copy; {{ new Date().getFullYear() }} {{ $t("footer.copyright") }}
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup></script>
