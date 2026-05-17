// Docusaurus sidebar configuration
module.exports = {
  docsSidebar: [
    'intro',
    'getting-started',
    'architecture',
    {
      type: 'category',
      label: 'API Reference',
      items: ['api/overview'],
    },
    {
      type: 'category',
      label: 'Admin',
      items: ['admin/overview'],
    },
    {
      type: 'category',
      label: 'O\'qituvchi',
      items: ['teacher/overview'],
    },
    {
      type: 'category',
      label: 'Talaba',
      items: ['student/overview'],
    },
  ],
};
