// Onze monuments au trait, un par etape de la route, dans une boite de
// 200x200 posee sur une ligne de sol a y=200. L'ordre suit le trace :
// Nice, Marseille, Montpellier, Narbonne, Toulouse, Bordeaux,
// La Rochelle, Nantes, Angers, Rennes, Saint-Malo.
window.MONUMENTS = [
  { ville:'Nice', legende:'Le Negresco', traits:[
    'M 62 200 L 62 118 M 118 200 L 118 118',
    'M 62 118 A 28 28 0 0 1 118 118',
    'M 90 90 L 90 74',
    'M 74 200 L 74 160 M 90 200 L 90 160 M 106 200 L 106 160',
    'M 68 148 L 112 148',
    // palmier
    'M 150 200 Q 148 168 155 140',
    'M 155 140 Q 128 136 118 156',
    'M 155 140 Q 182 134 192 154',
    'M 155 140 Q 133 118 136 100',
    'M 155 140 Q 177 118 174 100',
    'M 155 140 Q 155 112 155 98',
    'M 155 140 Q 138 128 126 128',
    'M 155 140 Q 172 128 184 128'
  ]},

  { ville:'Marseille', legende:'Notre-Dame de la Garde', traits:[
    'M 52 200 L 52 152 L 148 152 L 148 200',
    'M 62 200 L 62 168 M 82 200 L 82 168 M 118 200 L 118 168 M 138 200 L 138 168',
    'M 86 152 L 86 74 L 114 74 L 114 152',
    'M 86 74 L 100 58 L 114 74',
    'M 100 58 L 100 42',
    'M 100 36 m -5 0 a 5 5 0 1 0 10 0 a 5 5 0 1 0 -10 0',
    'M 92 118 L 92 96 M 108 118 L 108 96'
  ]},

  { ville:'Montpellier', legende:'L\'arc de triomphe du Peyrou', traits:[
    'M 34 200 L 34 186 L 166 186 L 166 200',
    'M 44 186 L 44 92 L 156 92 L 156 186',
    'M 74 186 L 74 138 A 26 26 0 0 1 126 138 L 126 186',
    'M 56 186 L 56 100 M 144 186 L 144 100',
    'M 38 92 L 38 76 L 162 76 L 162 92 Z',
    'M 52 76 L 52 52 L 148 52 L 148 76',
    'M 46 52 L 154 52',
    'M 100 64 m -9 0 a 9 9 0 1 0 18 0 a 9 9 0 1 0 -18 0'
  ]},

  { ville:'Narbonne', legende:'Le palais des archeveques', traits:[
    'M 62 200 L 62 66 L 122 66 L 122 200',
    'M 56 66 L 56 48 L 70 48 L 70 58 L 84 58 L 84 48 L 98 48 L 98 58 L 112 58 L 112 48 L 126 48 L 126 66',
    'M 54 66 L 128 66 M 58 80 L 126 80',
    'M 80 152 L 80 116 A 12 12 0 0 1 104 116 L 104 152',
    'M 84 200 L 84 176 A 8 8 0 0 1 100 176 L 100 200',
    'M 130 200 L 130 106 L 168 106 L 168 200',
    'M 126 106 L 126 92 L 140 92 L 140 100 L 154 100 L 154 92 L 168 92 L 168 106',
    'M 142 162 L 142 136 A 7 7 0 0 1 156 136 L 156 162'
  ]},

  { ville:'Toulouse', legende:'Saint-Sernin', traits:[
    'M 46 200 L 46 158 L 154 158 L 154 200',
    'M 78 158 L 78 122 L 122 122 L 122 158',
    'M 82 122 L 82 94 L 118 94 L 118 122',
    'M 86 94 L 86 70 L 114 70 L 114 94',
    'M 86 70 L 100 44 L 114 70',
    'M 88 146 L 88 132 M 100 146 L 100 132 M 112 146 L 112 132',
    'M 92 116 L 92 102 M 108 116 L 108 102'
  ]},

  { ville:'Bordeaux', legende:'La porte Cailhau', traits:[
    'M 70 200 L 70 92 L 130 92 L 130 200',
    'M 64 92 L 100 46 L 136 92',
    'M 56 200 L 56 112 L 70 112',
    'M 130 112 L 144 112 L 144 200',
    'M 52 112 L 63 90 L 74 112',
    'M 126 112 L 137 90 L 148 112',
    'M 84 200 L 84 172 A 16 16 0 0 1 116 172 L 116 200',
    'M 88 130 L 88 110 M 112 130 L 112 110'
  ]},

  { ville:'La Rochelle', legende:'Les tours du port', traits:[
    'M 44 200 L 44 112 L 84 112 L 84 200',
    'M 40 112 L 64 76 L 88 112',
    'M 64 76 L 64 64',
    'M 116 200 L 116 134 L 156 134 L 156 200',
    'M 112 134 L 136 102 L 160 134',
    'M 56 180 L 56 158 M 72 180 L 72 158',
    'M 128 180 L 128 162 M 144 180 L 144 162',
    'M 88 196 L 112 196'
  ]},

  { ville:'Nantes', legende:"L'elephant des Machines", traits:[
    // corps
    'M 46 170 Q 42 126 88 126 L 132 126 Q 158 126 160 152 L 160 168',
    // pattes
    'M 56 168 L 56 200 M 84 172 L 84 200 M 122 172 L 122 200 M 152 168 L 152 200',
    // tete et trompe
    'M 160 152 Q 176 150 178 136',
    'M 178 136 Q 186 156 182 176 Q 180 190 188 196',
    // oreille
    'M 148 148 m -13 0 a 13 13 0 1 0 26 0 a 13 13 0 1 0 -26 0',
    // defense
    'M 172 168 Q 182 172 186 168',
    // nacelle sur le dos
    'M 70 126 L 70 104 L 126 104 L 126 126',
    'M 82 104 L 82 88 M 98 104 L 98 88 M 114 104 L 114 88',
    'M 74 88 L 122 88',
    // queue
    'M 46 152 Q 36 160 40 176'
  ]},

  { ville:'Angers', legende:'Le chateau', traits:[
    // trois tours a talus, decapitees comme celles du chateau
    'M 16 200 L 16 118 A 24 11 0 0 1 64 118 L 64 200',
    'M 76 200 L 76 106 A 24 11 0 0 1 124 106 L 124 200',
    'M 136 200 L 136 118 A 24 11 0 0 1 184 118 L 184 200',
    // la courtine entre les tours
    'M 64 200 L 64 134 L 76 134',
    'M 136 134 L 124 134 L 124 200',
    // l'appareil en bandes de schiste et de tuffeau
    'M 16 150 L 64 150 M 76 138 L 124 138 M 136 150 L 184 150',
    'M 16 174 L 64 174 M 136 174 L 184 174',
    'M 76 158 L 124 158',
    // la porte
    'M 88 200 L 88 178 A 12 12 0 0 1 112 178 L 112 200',
    // meurtrieres
    'M 40 130 L 40 118 M 160 130 L 160 118'
  ]},

  { ville:'Rennes', legende:'Les colombages', traits:[
    'M 58 200 L 58 104 L 142 104 L 142 200',
    'M 50 104 L 100 60 L 150 104',
    'M 58 148 L 142 148',
    'M 58 148 L 100 104 M 142 148 L 100 104',
    'M 58 200 L 100 148 M 142 200 L 100 148',
    'M 100 104 L 100 60',
    'M 88 200 L 88 168 L 112 168 L 112 200',
    'M 76 132 L 76 116 M 124 132 L 124 116'
  ]},

  { ville:'Saint-Malo', legende:'Les remparts', traits:[
    // la ville close, vue depuis la greve
    'M 12 184 L 12 150 L 188 150 L 188 184',
    'M 12 150 L 12 138 L 26 138 L 26 148 L 40 148 L 40 138 L 54 138 L 54 148 ' +
      'L 68 148 L 68 138 L 82 138 L 82 148 L 96 148 L 96 138 L 110 138 L 110 148 ' +
      'L 124 148 L 124 138 L 138 138 L 138 148 L 152 148 L 152 138 L 166 138 ' +
      'L 166 148 L 180 148 L 180 138 L 188 138 L 188 150',
    // les malouinieres derriere le rempart
    'M 40 138 L 40 96 L 68 96 L 68 138',
    'M 34 96 L 54 76 L 74 96',
    'M 130 138 L 130 102 L 156 102 L 156 138',
    'M 124 102 L 143 82 L 162 102',
    'M 48 130 L 48 112 M 60 130 L 60 112 M 138 130 L 138 116 M 150 130 L 150 116',
    // la fleche de Saint-Vincent
    'M 100 138 L 100 86 L 124 86 L 124 138',
    'M 100 86 L 112 38 L 124 86',
    'M 112 38 L 112 24 M 105 30 L 119 30',
    'M 106 128 L 106 106 M 118 128 L 118 106',
    // la mer devant les murs
    'M 0 190 Q 20 182 40 190 Q 60 198 80 190 Q 100 182 120 190 ' +
      'Q 140 198 160 190 Q 180 182 200 190',
    'M -6 202 Q 16 194 38 202 Q 60 210 82 202 Q 104 194 126 202 ' +
      'Q 148 210 170 202 Q 192 194 210 202'
  ]}
];
