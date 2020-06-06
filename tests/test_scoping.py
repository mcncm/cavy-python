from .test_interpreter import stmt_test_template

def test_simple_scope():
    stmt_test_template("""
    v <- 2;
    {
      v <- 3;
      print v;
    }
    print v;
    """,
    ['3', '2'])

def test_complex_scope():
    stmt_test_template("""
    v <- 2;
    u <- 10;
    print u;
    {
      v <- 3;
      print v;
      {
        u <- u + v;
        {
          print u * 2;
        }
      }

      {
        u <- 0;
        print u;
      }
    }
    print v;
    """,
    ['10', '3', '26', '0', '2'])
