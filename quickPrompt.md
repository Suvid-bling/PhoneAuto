### Prompt for Extracting Logout Account Info

**Adjust info_list in setting.py:**

1. **Update the list format**
   - Example: `"T1008-4508371212"` maps to `["4508371212", 8, "", ""]`
   - The number `8` is called the index

2. **Sort info_pool in ascending order** (low to high by index)

3. **Filter accounts** - Only select accounts with description:
   - `-100 账号退出登录,请删除或者重新登陆`
