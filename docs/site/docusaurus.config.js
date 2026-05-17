// @ts-check
/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'UniAnalytics PRO Docs',
  tagline: "O'zbekiston universitetlari uchun OLAP+ML BI platform",
  favicon: 'img/favicon.ico',
  url: 'https://docs.unianalytics.uz',
  baseUrl: '/',
  organizationName: 'Muhammadqodir-Khakimov',
  projectName: 'unianalytics-pro',
  i18n: {
    defaultLocale: 'uz',
    locales: ['uz', 'ru', 'en', 'qq'],
  },
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/Muhammadqodir-Khakimov/unianalytics-pro/edit/main/docs/site/',
        },
        theme: { customCss: require.resolve('./src/css/custom.css') },
      },
    ],
  ],
  themeConfig: {
    navbar: {
      title: 'UniAnalytics PRO',
      items: [
        { type: 'docSidebar', sidebarId: 'docsSidebar', position: 'left', label: 'Docs' },
        { href: 'https://github.com/Muhammadqodir-Khakimov/unianalytics-pro', label: 'GitHub', position: 'right' },
      ],
    },
    footer: { style: 'dark', copyright: `© ${new Date().getFullYear()} UniAnalytics PRO` },
  },
};
module.exports = config;
