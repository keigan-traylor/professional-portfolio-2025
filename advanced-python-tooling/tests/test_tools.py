from tools import managed_resource
def test_managed_resource():
    with managed_resource('x') as res:
        assert res['name'] == 'x'
