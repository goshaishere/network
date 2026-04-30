<template>
  <q-page padding>
    <div class="text-h6 q-mb-md">{{ $t("console.stubTitle") }}</div>
    <q-tabs v-model="tab" dense class="q-mb-md" align="left">
      <q-tab name="users" :label="$t('console.tabUsers')" />
      <q-tab name="groups" :label="$t('console.tabGroups')" />
      <q-tab name="orgs" :label="$t('console.tabOrgs')" />
      <q-tab name="communities" :label="$t('console.tabCommunities')" />
    </q-tabs>

    <q-tab-panels v-model="tab" animated>
      <q-tab-panel name="users" class="q-pa-none">
        <q-banner v-if="errorMsg" rounded dense class="bg-negative text-white q-mb-md">{{ errorMsg }}</q-banner>
        <q-linear-progress v-if="loadingUsers" indeterminate color="primary" class="q-mb-md" />
        <q-table v-else :rows="rows" :columns="userColumns" row-key="id" flat bordered>
          <template #body-cell-is_employee="props">
            <q-td :props="props">
              <q-toggle v-model="props.row.is_employee" @update:model-value="saveUserRow(props.row)" />
            </q-td>
          </template>
          <template #body-cell-is_staff="props">
            <q-td :props="props">
              <q-toggle v-model="props.row.is_staff" @update:model-value="saveUserRow(props.row)" />
            </q-td>
          </template>
          <template #body-cell-employment_kind="props">
            <q-td :props="props">
              <q-select
                v-model="props.row.employment_kind"
                dense
                outlined
                emit-value
                map-options
                :options="employmentKinds"
                @update:model-value="saveUserRow(props.row)"
              />
            </q-td>
          </template>
          <template #body-cell-department="props">
            <q-td :props="props">
              <q-select
                v-model="props.row.department"
                dense
                outlined
                clearable
                emit-value
                map-options
                :options="departmentOptions"
                @update:model-value="saveUserRow(props.row)"
              />
            </q-td>
          </template>
          <template #body-cell-permission_group_ids="props">
            <q-td :props="props">
              <q-select
                v-model="props.row.permission_group_ids"
                dense
                outlined
                multiple
                use-chips
                emit-value
                map-options
                :options="permissionGroupSelectOptions"
                @update:model-value="saveUserRow(props.row)"
              />
            </q-td>
          </template>
          <template #body-cell-effective_permission_slugs="props">
            <q-td :props="props">
              <span class="text-caption text-grey-5">{{
                (props.row.effective_permission_slugs || []).join(", ") || "—"
              }}</span>
            </q-td>
          </template>
        </q-table>
      </q-tab-panel>

      <q-tab-panel name="groups" class="q-pa-none">
        <q-banner v-if="groupsError" rounded dense class="bg-negative text-white q-mb-md">{{ groupsError }}</q-banner>
        <q-linear-progress v-if="loadingGroups" indeterminate color="primary" class="q-mb-md" />
        <div v-else class="q-gutter-y-md">
          <div class="text-subtitle2">{{ $t("console.groupsTitle") }}</div>
          <q-list bordered separator class="q-mb-md">
            <q-item v-for="g in groups" :key="g.id">
              <q-item-section>
                <q-item-label>{{ g.name }} ({{ g.slug }})</q-item-label>
                <q-item-label caption>{{ (g.permission_slugs || []).join(", ") }}</q-item-label>
                <q-item-label caption>{{ $t("console.groupMembers") }}: {{ (g.member_ids || []).join(", ") || "—" }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-btn flat dense color="primary" @click="openEditGroup(g)">{{ $t("console.edit") }}</q-btn>
              </q-item-section>
            </q-item>
          </q-list>
          <div class="row q-col-gutter-sm items-end">
            <q-input v-model="newGroupName" dense outlined class="col-12 col-sm-3" :label="$t('console.groupName')" />
            <q-input v-model="newGroupSlug" dense outlined class="col-12 col-sm-3" :label="$t('console.groupSlug')" />
            <q-select
              v-model="newGroupPerms"
              multiple
              dense
              outlined
              use-chips
              emit-value
              map-options
              class="col-12 col-sm-4"
              :options="catalogOptions"
              :label="$t('console.permissions')"
            />
            <q-btn color="primary" unelevated :loading="creatingGroup" @click="createGroup">
              {{ $t("console.createGroup") }}
            </q-btn>
          </div>
        </div>
      </q-tab-panel>

      <q-tab-panel name="orgs" class="q-pa-none">
        <q-banner v-if="orgsError" rounded dense class="bg-negative text-white q-mb-md">{{ orgsError }}</q-banner>
        <q-linear-progress v-if="loadingOrgs" indeterminate color="primary" class="q-mb-md" />
        <div v-else class="row q-col-gutter-lg">
          <div class="col-12 col-md-6">
            <div class="text-subtitle2 q-mb-sm">{{ $t("console.organizations") }}</div>
            <q-list bordered separator class="q-mb-md">
              <q-item v-for="o in organizations" :key="o.id">
                <q-item-section>{{ o.name }}</q-item-section>
              </q-item>
            </q-list>
            <div class="row q-col-gutter-sm items-end">
              <q-input v-model="newOrgName" dense outlined class="col" :label="$t('console.newOrgName')" />
              <q-btn color="primary" unelevated :loading="creatingOrg" @click="createOrganization">{{ $t("console.create") }}</q-btn>
            </div>
          </div>
          <div class="col-12 col-md-6">
            <div class="text-subtitle2 q-mb-sm">{{ $t("console.departments") }}</div>
            <q-select
              v-model="deptFilterOrgId"
              dense
              outlined
              emit-value
              map-options
              class="q-mb-sm"
              :options="orgSelectOptions"
              :label="$t('console.filterByOrg')"
              clearable
              @update:model-value="loadDepartments"
            />
            <q-list bordered separator class="q-mb-md">
              <q-item v-for="d in departments" :key="d.id">
                <q-item-section>{{ departmentLabel(d) }}</q-item-section>
              </q-item>
            </q-list>
            <div class="row q-col-gutter-sm items-end">
              <q-select
                v-model="newDeptOrgId"
                dense
                outlined
                emit-value
                map-options
                class="col-12"
                :options="orgSelectOptions"
                :label="$t('console.deptOrganization')"
              />
              <q-input v-model="newDeptName" dense outlined class="col-12" :label="$t('console.newDeptName')" />
              <q-btn color="primary" unelevated :loading="creatingDept" @click="createDepartment">{{ $t("console.create") }}</q-btn>
            </div>
          </div>
        </div>
      </q-tab-panel>

      <q-tab-panel name="communities" class="q-pa-none">
        <q-banner v-if="communitiesError" rounded dense class="bg-negative text-white q-mb-md">{{ communitiesError }}</q-banner>
        <q-linear-progress v-if="loadingCommunities" indeterminate color="primary" class="q-mb-md" />
        <q-table v-else :rows="communities" :columns="communityColumns" row-key="id" flat bordered>
          <template #body-cell-is_open="props">
            <q-td :props="props">
              <q-toggle
                :model-value="props.row.is_open"
                @update:model-value="(v) => patchCommunityOpen(props.row, v)"
              />
            </q-td>
          </template>
          <template #body-cell-actions="props">
            <q-td :props="props">
              <q-btn dense flat color="primary" @click="openCommunityPosts(props.row)">{{ $t("console.posts") }}</q-btn>
            </q-td>
          </template>
        </q-table>
      </q-tab-panel>
    </q-tab-panels>

    <q-dialog v-model="editGroupOpen">
      <q-card style="min-width: 360px">
        <q-card-section class="text-h6">{{ $t("console.editGroupTitle") }}</q-card-section>
        <q-card-section v-if="editGroup">
          <q-select
            v-model="editGroup.permission_slugs"
            multiple
            dense
            outlined
            use-chips
            emit-value
            map-options
            class="q-mb-md"
            :options="catalogOptions"
            :label="$t('console.permissions')"
          />
          <q-select
            v-model="editGroup.member_ids"
            multiple
            dense
            outlined
            use-chips
            emit-value
            map-options
            :options="userMemberOptions"
            :label="$t('console.groupMembers')"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat :label="$t('console.cancel')" @click="editGroupOpen = false" />
          <q-btn color="negative" flat :label="$t('console.deleteGroup')" @click="deleteEditedGroup" />
          <q-btn color="primary" :label="$t('console.save')" :loading="savingGroup" @click="saveEditedGroup" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="postsDialogOpen">
      <q-card style="min-width: 480px">
        <q-card-section class="text-h6">{{ $t("console.communityPostsTitle") }}</q-card-section>
        <q-card-section>
          <q-linear-progress v-if="loadingPosts" indeterminate color="primary" class="q-mb-md" />
          <q-list v-else bordered separator>
            <q-item v-for="p in communityPosts" :key="p.id">
              <q-item-section>
                <q-item-label class="text-body2">{{ p.body }}</q-item-label>
                <q-item-label caption>{{ p.author_email }} · {{ p.created_at }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-btn dense flat color="negative" @click="deletePost(p.id)">{{ $t("console.deletePost") }}</q-btn>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat :label="$t('console.close')" @click="postsDialogOpen = false" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useQuasar } from "quasar";
import { useI18n } from "vue-i18n";
import { api } from "@/api/client";

interface AdminUserRow {
  id: number;
  email: string;
  display_name: string;
  is_staff: boolean;
  is_employee: boolean;
  employment_kind: "" | "internal" | "partner";
  department: number | null;
  permission_groups: { id: number; name: string; slug: string }[];
  permission_group_ids: number[];
  effective_permission_slugs: string[];
}

interface PermissionGroupRow {
  id: number;
  name: string;
  slug: string;
  description: string;
  permission_slugs: string[];
  member_ids: number[];
}

interface OrganizationRow {
  id: number;
  name: string;
}

interface DepartmentRow {
  id: number;
  organization: number;
  parent: number | null;
  name: string;
}

interface CommunityRow {
  id: number;
  name: string;
  slug: string;
  description: string;
  is_open: boolean;
  members_count: number;
  posts_count: number;
}

interface CommunityPostRow {
  id: number;
  author_email: string;
  body: string;
  created_at: string;
}

const { t } = useI18n();
const $q = useQuasar();
const tab = ref<"users" | "groups" | "orgs" | "communities">("users");
const loadingUsers = ref(true);
const loadingGroups = ref(false);
const loadingOrgs = ref(false);
const loadingCommunities = ref(false);
const loadingPosts = ref(false);
const errorMsg = ref("");
const groupsError = ref("");
const orgsError = ref("");
const communitiesError = ref("");
const rows = ref<AdminUserRow[]>([]);
const groups = ref<PermissionGroupRow[]>([]);
const organizations = ref<OrganizationRow[]>([]);
const departments = ref<DepartmentRow[]>([]);
const deptFilterOrgId = ref<number | null>(null);
const newOrgName = ref("");
const newDeptName = ref("");
const newDeptOrgId = ref<number | null>(null);
const creatingOrg = ref(false);
const creatingDept = ref(false);
const communities = ref<CommunityRow[]>([]);
const catalogOptions = ref<{ label: string; value: string }[]>([]);
const newGroupName = ref("");
const newGroupSlug = ref("");
const newGroupPerms = ref<string[]>([]);
const creatingGroup = ref(false);

const editGroupOpen = ref(false);
const editGroup = ref<PermissionGroupRow | null>(null);
const savingGroup = ref(false);

const postsDialogOpen = ref(false);
const postsCommunityId = ref<number | null>(null);
const communityPosts = ref<CommunityPostRow[]>([]);

const employmentKinds = [
  { label: "-", value: "" },
  { label: "internal", value: "internal" },
  { label: "partner", value: "partner" },
];

const userColumns = computed(() => [
  { name: "id", label: "ID", field: "id", align: "left" as const },
  { name: "email", label: "Email", field: "email", align: "left" as const },
  { name: "display_name", label: t("console.displayNameCol"), field: "display_name", align: "left" as const },
  { name: "is_staff", label: "Admin", field: "is_staff", align: "left" as const },
  { name: "is_employee", label: "Employee", field: "is_employee", align: "left" as const },
  { name: "employment_kind", label: t("console.kindCol"), field: "employment_kind", align: "left" as const },
  { name: "department", label: t("console.department"), field: "department", align: "left" as const },
  {
    name: "permission_group_ids",
    label: t("console.permissionGroups"),
    field: "permission_group_ids",
    align: "left" as const,
  },
  {
    name: "effective_permission_slugs",
    label: t("console.effectivePerms"),
    field: "effective_permission_slugs",
    align: "left" as const,
  },
]);

const communityColumns = computed(() => [
  { name: "id", label: "ID", field: "id", align: "left" as const },
  { name: "name", label: t("console.communityName"), field: "name", align: "left" as const },
  { name: "slug", label: "Slug", field: "slug", align: "left" as const },
  { name: "members_count", label: t("console.membersCount"), field: "members_count", align: "right" as const },
  { name: "posts_count", label: t("console.postsCount"), field: "posts_count", align: "right" as const },
  { name: "is_open", label: t("console.isOpen"), field: "is_open", align: "left" as const },
  { name: "actions", label: "", field: "actions", align: "right" as const },
]);

const orgSelectOptions = computed(() =>
  organizations.value.map((o) => ({ label: o.name, value: o.id }))
);

const departmentOptions = computed(() =>
  departments.value.map((d) => ({
    label: departmentLabel(d),
    value: d.id,
  }))
);

const permissionGroupSelectOptions = computed(() =>
  groups.value.map((g) => ({ label: `${g.name} (${g.slug})`, value: g.id }))
);

const userMemberOptions = computed(() =>
  rows.value.map((u) => ({ label: `${u.email}`, value: u.id }))
);

function departmentLabel(d: DepartmentRow) {
  const org = organizations.value.find((o) => o.id === d.organization);
  return org ? `${org.name} / ${d.name}` : d.name;
}

async function loadUsers() {
  const { data } = await api.get<AdminUserRow[]>("/admin/users/");
  rows.value = data.map((r) => ({
    ...r,
    permission_group_ids: r.permission_group_ids?.length
      ? r.permission_group_ids
      : (r.permission_groups || []).map((g) => g.id),
  }));
}

async function loadGroupsPanel() {
  loadingGroups.value = true;
  groupsError.value = "";
  try {
    const [cat, grp] = await Promise.all([
      api.get<{ slug: string; name: string }[]>("/admin/permission-catalog/"),
      api.get<PermissionGroupRow[]>("/admin/permission-groups/"),
    ]);
    catalogOptions.value = cat.data.map((x) => ({ label: `${x.slug} — ${x.name}`, value: x.slug }));
    groups.value = grp.data;
  } catch {
    groupsError.value = t("console.loadGroupsError");
  } finally {
    loadingGroups.value = false;
  }
}

async function loadOrgsPanel() {
  loadingOrgs.value = true;
  orgsError.value = "";
  try {
    const { data } = await api.get<OrganizationRow[]>("/admin/organizations/");
    organizations.value = data;
    await loadDepartments();
  } catch {
    orgsError.value = t("console.loadOrgsError");
  } finally {
    loadingOrgs.value = false;
  }
}

async function loadDepartments() {
  const params = deptFilterOrgId.value != null ? { organization: deptFilterOrgId.value } : {};
  const { data } = await api.get<DepartmentRow[]>("/admin/departments/", { params });
  departments.value = data;
}

async function loadCommunitiesPanel() {
  loadingCommunities.value = true;
  communitiesError.value = "";
  try {
    const { data } = await api.get<CommunityRow[]>("/admin/communities/");
    communities.value = data;
  } catch {
    communitiesError.value = t("console.loadCommunitiesError");
  } finally {
    loadingCommunities.value = false;
  }
}

async function saveUserRow(row: AdminUserRow) {
  try {
    await api.patch("/admin/users/", {
      id: row.id,
      is_staff: row.is_staff,
      is_employee: row.is_employee,
      employment_kind: row.employment_kind,
      department: row.department,
      permission_group_ids: row.permission_group_ids,
    });
    await loadUsers();
  } catch {
    errorMsg.value = t("common.stubBody");
  }
}

async function createGroup() {
  if (!newGroupName.value.trim() || !newGroupSlug.value.trim()) return;
  creatingGroup.value = true;
  try {
    await api.post("/admin/permission-groups/", {
      name: newGroupName.value.trim(),
      slug: newGroupSlug.value.trim().toLowerCase().replaceAll(/\s+/g, "-"),
      description: "",
      permission_slugs: newGroupPerms.value,
      member_ids: [],
    });
    newGroupName.value = "";
    newGroupSlug.value = "";
    newGroupPerms.value = [];
    await loadGroupsPanel();
  } catch {
    groupsError.value = t("console.loadGroupsError");
  } finally {
    creatingGroup.value = false;
  }
}

function openEditGroup(g: PermissionGroupRow) {
  editGroup.value = {
    ...g,
    permission_slugs: [...(g.permission_slugs || [])],
    member_ids: [...(g.member_ids || [])],
  };
  editGroupOpen.value = true;
}

async function saveEditedGroup() {
  if (!editGroup.value) return;
  savingGroup.value = true;
  try {
    await api.patch(`/admin/permission-groups/${editGroup.value.id}/`, {
      permission_slugs: editGroup.value.permission_slugs,
      member_ids: editGroup.value.member_ids,
    });
    editGroupOpen.value = false;
    await loadGroupsPanel();
    await loadUsers();
  } catch {
    groupsError.value = t("console.loadGroupsError");
  } finally {
    savingGroup.value = false;
  }
}

async function deleteEditedGroup() {
  if (!editGroup.value) return;
  $q.dialog({
    title: t("console.deleteGroupConfirmTitle"),
    message: t("console.deleteGroupConfirmBody"),
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/admin/permission-groups/${editGroup.value!.id}/`);
      editGroupOpen.value = false;
      await loadGroupsPanel();
      await loadUsers();
    } catch {
      groupsError.value = t("console.loadGroupsError");
    }
  });
}

async function createOrganization() {
  const name = newOrgName.value.trim();
  if (!name) return;
  creatingOrg.value = true;
  try {
    await api.post("/admin/organizations/", { name });
    newOrgName.value = "";
    await loadOrgsPanel();
  } catch {
    orgsError.value = t("console.loadOrgsError");
  } finally {
    creatingOrg.value = false;
  }
}

async function createDepartment() {
  if (newDeptOrgId.value == null || !newDeptName.value.trim()) return;
  creatingDept.value = true;
  try {
    await api.post("/admin/departments/", {
      organization: newDeptOrgId.value,
      parent: null,
      name: newDeptName.value.trim(),
    });
    newDeptName.value = "";
    await loadDepartments();
  } catch {
    orgsError.value = t("console.loadOrgsError");
  } finally {
    creatingDept.value = false;
  }
}

async function patchCommunityOpen(row: CommunityRow, isOpen: boolean) {
  try {
    await api.patch(`/admin/communities/${row.id}/`, { is_open: isOpen });
    await loadCommunitiesPanel();
  } catch {
    communitiesError.value = t("console.loadCommunitiesError");
  }
}

function openCommunityPosts(row: CommunityRow) {
  postsCommunityId.value = row.id;
  postsDialogOpen.value = true;
  void loadCommunityPosts();
}

async function loadCommunityPosts() {
  if (postsCommunityId.value == null) return;
  loadingPosts.value = true;
  try {
    const { data } = await api.get<CommunityPostRow[]>(`/admin/communities/${postsCommunityId.value}/posts/`);
    communityPosts.value = data;
  } catch {
    communityPosts.value = [];
  } finally {
    loadingPosts.value = false;
  }
}

async function deletePost(postId: number) {
  try {
    await api.delete(`/admin/communities/posts/${postId}/`);
    await loadCommunityPosts();
    await loadCommunitiesPanel();
  } catch {
    communitiesError.value = t("console.loadCommunitiesError");
  }
}

watch(tab, (v) => {
  if (v === "groups") void loadGroupsPanel();
  if (v === "orgs") void loadOrgsPanel();
  if (v === "communities") void loadCommunitiesPanel();
});

onMounted(async () => {
  loadingUsers.value = true;
  errorMsg.value = "";
  try {
    await loadOrgsPanel();
  } catch {
    orgsError.value = t("console.loadOrgsError");
  }
  try {
    await loadGroupsPanel();
  } catch {
    groupsError.value = t("console.loadGroupsError");
  }
  try {
    await loadUsers();
  } catch {
    errorMsg.value = t("common.stubBody");
  } finally {
    loadingUsers.value = false;
  }
});
</script>
