import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      light: '#64EEBB',
      main: '#00C4B4',  // Turchese brillante
      dark: '#00A896',
      contrastText: '#fff',
    },
    secondary: {
      light: '#FF88A2',
      main: '#FF5678',  // Rosa accattivante
      dark: '#E63E68',
      contrastText: '#fff',
    },
    success: {
      main: '#66BB6A',  // Verde brillante 
      light: '#A5D6A7',
      dark: '#388E3C',
    },
    error: {
      main: '#FF8A65',  // Arancione/rosso più soft per non spaventare
      light: '#FFAB91',
      dark: '#E64A19',
    },
    warning: {
      main: '#FFCA28',  // Giallo ambra
      light: '#FFE082',
      dark: '#FFA000',
    },
    info: {
      main: '#29B6F6',  // Azzurro chiaro
      light: '#81D4FA',
      dark: '#0288D1',
    },
    background: {
      default: '#FBFCFF',  // Bianco con leggera tinta blu
      paper: '#ffffff',
    },
    text: {
      primary: '#43484F',  // Grigio scuro invece di nero puro
      secondary: '#5B6571',
    }
  },
  typography: {
    fontFamily: [
      'Comic Neue',  // Font simile a Comic Sans ma più moderno
      'Roboto',
      '"Baloo 2"',  // Font rotondo e amichevole
      'Nunito',     // Font rotondo con buona leggibilità
      'Arial',
      'sans-serif',
    ].join(','),
    h4: {
      fontWeight: 700,
      fontSize: '2.25rem',
      letterSpacing: '0.02em',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.75rem',
      letterSpacing: '0.01em',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    button: {
      fontWeight: 600,
      textTransform: 'none',  // No all caps for better readability for children
    }
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,  // Bottoni più arrotondati
          padding: '10px 20px',
          boxShadow: '0 3px 5px rgba(0,0,0,0.1)',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-3px)',
            boxShadow: '0 6px 10px rgba(0,0,0,0.15)',
          },
          '&:active': {
            transform: 'translateY(0)',
          }
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,  // Card più arrotondate
          boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
          overflow: 'visible',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
    MuiRadio: {
      styleOverrides: {
        root: {
          '& .MuiSvgIcon-root': {
            fontSize: '1.5rem',  // Radio button più grandi
          },
        },
      },
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0 2px 4px rgba(0,0,0,0.05)',
    '0 4px 8px rgba(0,0,0,0.07)',
    '0 6px 12px rgba(0,0,0,0.08)',
    '0 8px 16px rgba(0,0,0,0.1)',
    // ... definisci altre ombre se necessario
    '0 20px 40px rgba(0,0,0,0.15)', // Ombra più forte
  ],
});

export default theme;
